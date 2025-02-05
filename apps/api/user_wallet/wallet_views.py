from .wallet_serializers import WalletSerializer, PositiveBalanceWalletsSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from project.permissions import ZUserTokenPermission
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from project.language import translator
from rest_framework import status
from .wallet_models import Wallet


class WalletViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    """
    Представление для управления кошельками.
    """
    serializer_class = WalletSerializer
    permission_classes = [ZUserTokenPermission]

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
            raise ValidationError(translator(
                "Кошелёк для данного пользователя уже существует.",
                "The wallet for this user already exists.",
                self.request
            ))

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
    permission_classes = [ZUserTokenPermission]

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

    def destroy(self, request, *args, **kwargs):
        """
        Мягкое удаление кошелька: устанавливает is_active=False.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на удаление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": translator(
                    "У вас нет прав на удаление этого кошелька.",
                    "You don't have rights to delete this wallet.",
                    self.request
                )},
                status=403
            )

        # Мягкое удаление
        instance.status = "deleted"
        instance.is_active = False
        instance.save(update_fields=["is_active", "status"])

        return Response({"detail": translator(
            "Кошелёк успешно деактивирован.",
            "The wallet has been successfully deactivated.",
            self.request
        )}, status=204)

    def activate(self, request, *args, **kwargs):
        """
        Восстанавливает (активирует) только неактивные кошельки (is_active=False).
        """
        instance = self.get_object()

        # Проверяем, является ли кошелек неактивным
        if instance.is_active:
            return Response(
                {"detail": translator(
                    "Этот кошелёк уже активен.",
                    "This wallet is already active.",
                    self.request
                )},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, имеет ли пользователь права на восстановление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": translator(
                    "У вас нет прав на восстановление этого кошелька.",
                    "You do not have the rights to restore this wallet.",
                    self.request
                )},
                status=status.HTTP_403_FORBIDDEN
            )

        # Восстанавливаем кошелёк
        instance.status = "active"
        instance.is_active = True
        instance.save(update_fields=["is_active", "status"])

        return Response({"detail": translator(
            "Кошелёк успешно восстановлен.",
            "The wallet has been successfully restored.",
            self.request
        )}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Обновляет данные кошелька.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на редактирование
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": translator(
                    "У вас нет прав на редактирование этого кошелька.",
                    "You do not have the rights to edit this wallet.",
                    self.request
                )},
                status=403
            )

        # Обновление кошелька
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class PositiveBalanceWalletsView(APIView):
    permission_classes = [ZUserTokenPermission]

    def get(self, request, *args, **kwargs):
        """
        Возвращает список кошельков с положительным балансом.
        Доступно только для пользователей is_staff.
        """
        if not request.user.is_staff:
            raise PermissionDenied(translator(
                "Доступ разрешён только администраторам.",
                "Access is allowed only to administrators.",
                self.request
            ))

        # Фильтруем кошельки с положительным балансом
        accounts = Wallet.objects.filter(balance__gt=0)
        serializer = PositiveBalanceWalletsSerializer(accounts, many=True)
        return Response(serializer.data)
