from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .refill_model import Refill
from .refill_serializer import RefillSerializer
from ..payment_account.payment_model import PaymentAccount


class RefillViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = RefillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только активные пополнения для текущего пользователя.
        Администраторы видят все пополнения.
        """
        user = self.request.user
        account_id = self.kwargs['account_id']

        if user.is_staff:  # Администратор видит все пополнения
            return Refill.objects.filter(account_id=account_id)

        # Проверка на владельца аккаунта
        if not PaymentAccount.objects.filter(account_id=account_id, user=user).exists():
            raise PermissionDenied("У вас нет доступа к этому платёжному аккаунту.")

        return Refill.objects.filter(is_active=True, account_id=account_id)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создает пополнение и увеличивает баланс платёжного аккаунта.
        """
        account_id = self.kwargs['account_id']
        account = PaymentAccount.objects.select_for_update().get(pk=account_id)  # Блокируем запись для исключения гонок

        # Проверка на владельца аккаунта
        if account.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого аккаунта.")

        # Увеличиваем баланс аккаунта
        amount = serializer.validated_data['amount']
        account.balance += amount
        account.save()

        # Создаем пополнение
        serializer.save(account_id=account_id)

    def get_object_for_restore(self):
        """
        Получает объект Refill без фильтрации по is_active.
        """
        # Мы ищем только по pk, без фильтрации по is_active на этом этапе
        queryset = Refill.objects.filter(pk=self.kwargs["pk"])

        # Проверим, существует ли объект и является ли он мягко удалённым
        refill = queryset.first()  # Используем first(), чтобы избежать исключений, если объект не найден

        if refill is None:
            raise NotFound("Пополнение не найдено.")

        # Если объект существует, но он активен, то не нужно восстанавливать
        if refill.is_active:
            raise ValidationError({"detail": "Пополнение уже активно."})

        return refill

    @action(detail=True, methods=['post'])
    def destroy(self, request, account_id=None, pk=None):
        """
        Мягкое удаление пополнения.
        """
        # Ищем объект пополнения
        try:
            refill = Refill.objects.get(pk=pk)
        except Refill.DoesNotExist:
            raise NotFound("Пополнение не найдено.")

        # Проверка, что пополнение принадлежит указанному аккаунту и владельцу
        if refill.account_id != account_id:
            raise PermissionDenied("Это пополнение не принадлежит указанному аккаунту.")
        if refill.account.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого аккаунта.")

        # Если пополнение уже удалено, возвращаем ошибку
        if not refill.is_active:
            return Response({"detail": "Пополнение уже удалено."}, status=400)

        # Мягко удаляем пополнение
        refill.delete()

        return Response(
            {"detail": f"Пополнение {refill.refill_id} успешно удалено."},
            status=200
        )

    @action(detail=True, methods=['post'])
    def restore(self, request, account_id=None, pk=None):
        """
        Восстанавливает мягко удалённое пополнение.
        """
        # Ищем объект без фильтрации
        refill = self.get_object_for_restore()

        # Проверка, что пополнение принадлежит указанному аккаунту и владельцу
        if refill.account_id != account_id:
            raise PermissionDenied("Это пополнение не принадлежит указанному аккаунту.")
        if refill.account.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого аккаунта.")

        # Проверяем, активно ли пополнение
        if refill.is_active:
            return Response({"detail": "Пополнение уже активно."}, status=400)

        # Восстанавливаем пополнение
        refill.restore()
        return Response(
            {"detail": f"Пополнение {refill.refill_id} успешно восстановлено."},
            status=200
        )
