from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .wallet_refill_models import WalletRefill
from .wallet_refill_serializers import WalletRefillSerializer
from ..user_wallet.wallet_models import Wallet


class WalletRefillViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = WalletRefillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только активные пополнения для текущего пользователя.
        Администраторы видят все пополнения.
        """
        user = self.request.user
        # wallet_id = self.kwargs['wallet_id']

        if user.is_staff:  # Администратор видит все пополнения
            # return WalletRefill.objects.filter(wallet_id=wallet_id)
            return WalletRefill.objects.filter()

        # Проверка на владельца кошелька
        # if not Wallet.objects.filter(wallet_id=wallet_id, user=user).exists():
        if not Wallet.objects.filter(user=user).exists():
            raise PermissionDenied("У вас нет доступа к этому платёжному кошельку.")

        # return WalletRefill.objects.filter(is_active=True, wallet_id=wallet_id)
        return WalletRefill.objects.filter(is_active=True)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создает пополнение и увеличивает баланс платёжного кошелька.
        """
        wallet_id = self.kwargs['wallet_id']
        wallet = Wallet.objects.select_for_update().get(pk=wallet_id)  # Блокируем запись для исключения гонок

        # Проверка на владельца кошелька
        if wallet.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого кошелька.")

        # Увеличиваем баланс кошелька
        amount = serializer.validated_data['amount']
        wallet.balance += amount
        wallet.save()

        # Создаем пополнение
        serializer.save(wallet_id=wallet_id)

    def get_object_for_restore(self):
        """
        Получает объект Refill без фильтрации по is_active.
        """
        # Мы ищем только по pk, без фильтрации по is_active на этом этапе
        queryset = WalletRefill.objects.filter(pk=self.kwargs["pk"])

        # Проверим, существует ли объект и является ли он мягко удалённым
        refill = queryset.first()  # Используем first(), чтобы избежать исключений, если объект не найден

        if refill is None:
            raise NotFound("Пополнение не найдено.")

        # Если объект существует, но он активен, то не нужно восстанавливать
        if refill.is_active:
            raise ValidationError({"detail": "Пополнение уже активно."})

        return refill

    @action(detail=True, methods=['post'])
    def destroy(self, request, wallet_id=None, pk=None):
        """
        Мягкое удаление пополнения.
        """
        # Ищем объект пополнения
        try:
            refill = WalletRefill.objects.get(pk=pk)
        except WalletRefill.DoesNotExist:
            raise NotFound("Пополнение не найдено.")

        # Проверка, что пополнение принадлежит указанному кошельку и владельцу
        if refill.wallet_id != wallet_id:
            raise PermissionDenied("Это пополнение не принадлежит указанному кошельку.")
        if refill.wallet.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого кошелька.")

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
    def restore(self, request, wallet_id=None, pk=None):
        """
        Восстанавливает мягко удалённое пополнение.
        """
        # Ищем объект без фильтрации
        refill = self.get_object_for_restore()

        # Проверка, что пополнение принадлежит указанному кошельку и владельцу
        if refill.wallet_id != wallet_id:
            raise PermissionDenied("Это пополнение не принадлежит указанному кошельку.")
        if refill.wallet.user != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого кошелька.")

        # Проверяем, активно ли пополнение
        if refill.is_active:
            return Response({"detail": "Пополнение уже активно."}, status=400)

        # Восстанавливаем пополнение
        refill.restore()
        return Response(
            {"detail": f"Пополнение {refill.refill_id} успешно восстановлено."},
            status=200
        )
