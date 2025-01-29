from .wallet_serializers import WalletSerializer, PositiveBalanceWalletsSerializer
from .wallet_models import Wallet
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.views import APIView


class WalletViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    """
    Представление для управления кошельками.
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только кошельки текущего авторизованного пользователя.
        Администраторы видят все кошельки.
        """
        user = self.request.user
        if user.is_staff:  # Администратор видит все кошельки
            return Wallet.objects.all()
        # Обычный пользователь видит только свои кошельки
        return Wallet.objects.filter(user=user, is_active=True)

    def perform_create(self, serializer):
        user = self.request.user

        # Проверяем, существует ли уже кошелёк пользователя
        if Wallet.objects.filter(user=user).exists():
            raise ValidationError(f"Кошелёк для данного пользователя уже существует.")

        # Создаём новый кошелёк
        serializer.save(user=user, is_active=True, balance=0.000000)

class WalletDetailViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Представление для управления кошельками.
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только кошельки текущего авторизованного пользователя.
        Администраторы видят все кошельки.
        """
        user = self.request.user
        if user.is_staff:  # Администратор видит все кошельки
            return Wallet.objects.all()
        # Обычный пользователь видит только свои кошельки
        return Wallet.objects.filter(user=user)

    # def perform_create(self, serializer):
    #     """
    #     Создаёт новый кошелёк для пользователя.
    #     """
    #     user = self.request.user
    #
    #     # Проверяем, существует ли уже кошелёк пользователя
    #     if Wallet.objects.filter(user=user).exists():
    #         raise ValidationError(f"Кошелёк для данного пользователя уже существует.")
    #
    #     # Создаём новый платёжный аккаунт
    #     serializer.save(user=user, is_active=True, balance=0.000000)

    def destroy(self, request, *args, **kwargs):
        """
        Мягкое удаление кошелька: устанавливает is_active=False.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на удаление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на удаление этого кошелька."},
                status=403
            )

        # Мягкое удаление
        instance.is_active = False
        instance.save()

        return Response({"detail": "Кошелёк успешно деактивирован."}, status=204)

    def activate(self, request, *args, **kwargs):
        """
        Мягкое восстановление кошелька: устанавливает is_active=True.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на восстановление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на восстановление этого кошелька."},
                status=403
            )

        # Мягкое восстановление
        instance.is_active = True
        instance.save()

        return Response({"detail": "Кошелёк успешно восстановлен."}, status=204)

    def update(self, request, *args, **kwargs):
        """
        Обновляет данные кошелька.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на редактирование
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на редактирование этого кошелька."},
                status=403
            )

        # Обновление кошелька
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class PositiveBalanceWalletsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Возвращает список кошельков с положительным балансом.
        Доступно только для пользователей is_staff.
        """
        if not request.user.is_staff:
            raise PermissionDenied("Доступ разрешён только администраторам.")

        # Фильтруем кошельки с положительным балансом
        accounts = Wallet.objects.filter(balance__gt=0)
        serializer = PositiveBalanceWalletsSerializer(accounts, many=True)
        return Response(serializer.data)
