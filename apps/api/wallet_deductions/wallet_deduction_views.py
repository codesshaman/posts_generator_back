from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .wallet_deduction_models import WalletDeduction
from .wallet_deduction_serializers import WalletDeductionSerializer
from ..payment_account.payment_models import PaymentAccount


class DeductionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = WalletDeductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только активные транзакции для текущего пользователя.
        Администраторы видят все транзакции.
        """
        user = self.request.user
        account_id = self.kwargs['account_id']

        if user.is_staff:  # Администратор видит все транзакции
            return WalletDeduction.objects.filter(account_id=account_id)

        # Проверка на владельца аккаунта
        if not PaymentAccount.objects.filter(account_id=account_id, user=user).exists():
            raise PermissionDenied("У вас нет доступа к этому платёжному аккаунту.")

        return WalletDeduction.objects.filter(is_active=True, account_id=account_id)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создает списание и уменьшает баланс платёжного аккаунта.
        """
        account_id = self.kwargs['account_id']
        account = PaymentAccount.objects.select_for_update().get(pk=account_id)  # Блокируем запись для исключения гонок

        # Проверка на владельца аккаунта
        if account.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого аккаунта.")

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
        queryset = WalletDeduction.objects.all()  # Убираем фильтрацию
        try:
            return queryset.get(pk=self.kwargs["pk"])
        except WalletDeduction.DoesNotExist:
            raise NotFound("Транзакция не найдена.")

    @action(detail=True, methods=['post'])
    def destroy(self, request, account_id=None, pk=None):
        """
        Мягкое удаление транзакции.
        """
        # Ищем объект транзакции
        try:
            deduction = WalletDeduction.objects.get(pk=pk)
        except WalletDeduction.DoesNotExist:
            raise NotFound("Транзакция не найдена.")

        # Проверка, что транзакция принадлежит указанному аккаунту и владельцу
        if deduction.account_id != account_id:
            raise PermissionDenied("Эта транзакция не принадлежит указанному аккаунту.")
        if deduction.account.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого аккаунта.")

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

        # Проверка, что транзакция принадлежит указанному аккаунту и владельцу
        if deduction.account_id != account_id:
            raise PermissionDenied("Эта транзакция не принадлежит указанному аккаунту.")
        if deduction.account.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого аккаунта.")

        # Проверяем, активна ли транзакция
        if deduction.is_active:
            return Response({"detail": "Транзакция уже активна."}, status=400)

        # Восстанавливаем транзакцию
        deduction.restore()
        return Response(
            {"detail": f"Транзакция {deduction.deduction_id} успешно восстановлена."},
            status=200
        )
