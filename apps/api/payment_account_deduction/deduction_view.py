from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .deduction_model import Deduction
from .deduction_serializer import DeductionSerializer
from ..payment_account.payment_model import PaymentAccount


class DeductionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        По умолчанию возвращает только активные транзакции.
        """
        account_id = self.kwargs['account_id']
        # Проверяем, существует ли указанный аккаунт
        if not PaymentAccount.objects.filter(pk=account_id).exists():
            raise NotFound("Платёжный аккаунт не найден.")
        return Deduction.objects.filter(is_active=True, account_id=account_id)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создает списание и уменьшает баланс платёжного аккаунта.
        """
        account_id = self.kwargs['account_id']
        account = PaymentAccount.objects.select_for_update().get(pk=account_id)  # Блокируем запись для исключения гонок

        # Проверяем, достаточно ли средств
        amount = serializer.validated_data['amount']
        if account.balance < amount:
            raise ValidationError({"detail": "Недостаточно средств на платёжном аккаунте."})

        # Уменьшаем баланс аккаунта
        account.balance -= amount
        account.save()

        # Создаем списание
        serializer.save(account_id=account_id)

    def get_object_for_restore(self):
        """
        Получает объект Deduction без фильтрации по is_active.
        """
        queryset = Deduction.objects.all()  # Убираем фильтрацию
        try:
            return queryset.get(pk=self.kwargs["pk"])
        except Deduction.DoesNotExist:
            raise NotFound("Транзакция не найдена.")

    @action(detail=True, methods=['post'])
    def destroy(self, request, account_id=None, pk=None):
        """
        Мягкое удаление транзакции.
        """
        # Ищем объект транзакции
        try:
            deduction = Deduction.objects.get(pk=pk)
        except Deduction.DoesNotExist:
            raise NotFound("Транзакция не найдена.")

        # Проверяем, принадлежит ли транзакция указанному аккаунту
        if deduction.account_id != account_id:
            raise PermissionDenied("Эта транзакция не принадлежит указанному аккаунту.")

        # Если транзакция уже удалена, возвращаем ошибку
        if not deduction.is_active:
            return Response({"detail": "Транзакция уже удалена."}, status=400)

        # Мягко удаляем транзакцию
        deduction.delete()

        return Response(
            {"detail": f"Транзакция {deduction.deduction_id} успешно удалена."},
            status=200
        )

    @action(detail=True, methods=['post'])
    def restore(self, request, account_id=None, pk=None):
        """
        Восстанавливает мягко удалённую транзакцию.
        """
        # Ищем объект без фильтрации
        deduction = self.get_object_for_restore()

        # Проверяем, принадлежит ли транзакция указанному аккаунту
        if deduction.account_id != account_id:
            raise PermissionDenied("Эта транзакция не принадлежит указанному аккаунту.")

        # Проверяем, активна ли транзакция
        if deduction.is_active:
            return Response({"detail": "Транзакция уже активна."}, status=400)

        # Восстанавливаем транзакцию
        deduction.restore()
        return Response(
            {"detail": f"Транзакция {deduction.deduction_id} успешно восстановлена."},
            status=200
        )
