from .payment_serializers import PaymentAccountSerializer, PositiveBalanceAccountsSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from project.permissions import ZUserTokenPermission
from rest_framework.permissions import  IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from .payment_models import PaymentAccount
from rest_framework.views import APIView
from project.language import translator


class PaymentAccountViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    """
    Представление для управления платёжными аккаунтами.
    """
    serializer_class = PaymentAccountSerializer
    permission_classes = [ZUserTokenPermission]

    def get_queryset(self):
        """
        Возвращает только платёжные аккаунты текущего авторизованного пользователя.
        Администраторы видят все аккаунты.
        """
        user = self.request.user
        if user.is_staff:  # Администратор видит все аккаунты
            return PaymentAccount.objects.all()
        # Обычный пользователь видит только свои аккаунты
        return PaymentAccount.objects.filter(user=user, is_active=True)

    def perform_create(self, serializer):
        user = self.request.user
        currency = serializer.validated_data.get('currency')  # Извлекаем валюту из данных

        # Проверяем, существует ли уже платёжный аккаунт с данной валютой для пользователя
        if PaymentAccount.objects.filter(user=user, currency=currency).exists():
            raise ValidationError(translator(
                "Платёжный аккаунт с этой валютой уже существует для данного пользователя.",
                "A billing account with this currency already exists for this user.",
                self.request
            ))

        # Создаём новый платёжный аккаунт
        serializer.save(user=user)

class PaymentAccountsViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Представление для управления платёжными аккаунтами.
    """
    serializer_class = PaymentAccountSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Возвращает только платёжные аккаунты текущего авторизованного пользователя.
        Администраторы видят все аккаунты.
        """
        user = self.request.user
        if user.is_staff:  # Администратор видит все аккаунты
            return PaymentAccount.objects.all()
        # Обычный пользователь видит только свои аккаунты
        return PaymentAccount.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        Создаёт платёжный аккаунт с проверкой уникальности валюты для пользователя.
        """
        user = self.request.user
        currency = serializer.validated_data.get('currency')  # Извлекаем валюту из данных

        # Проверяем, существует ли уже платёжный аккаунт с данной валютой для пользователя
        if PaymentAccount.objects.filter(user=user, currency=currency).exists():
            raise ValidationError(translator(
                "Платёжный аккаунт с этой валютой уже существует для данного пользователя.",
                "A billing account with this currency already exists for this user.",
                self.request
            ))

        # Создаём новый платёжный аккаунт
        serializer.save(user=user, is_active=True)

    def destroy(self, request, *args, **kwargs):
        """
        Мягкое удаление аккаунта: устанавливает is_active=False.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на удаление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": translator(
                    "У вас нет прав на удаление этого платёжного аккаунта.",
                    "You do not have the rights to delete this billing account.",
                    self.request
                )},
                status=403
            )

        # Мягкое удаление
        instance.is_active = False
        instance.save()

        return Response({"detail": translator(
            "Платёжный аккаунт успешно деактивирован.",
            "Billing account has been successfully deactivated.",
            self.request
        )}, status=204)

    def activate(self, request, *args, **kwargs):
        """
        Мягкое восстановление аккаунта: устанавливает is_active=True.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на восстановление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": translator(
                    "У вас нет прав на восстановление этого платёжного аккаунта.",
                    "You do not have the rights to restore this billing account.",
                    self.request
                )},
                status=403
            )

        # Мягкое восстановление
        instance.is_active = True
        instance.save()

        return Response({"detail": translator(
            "Платёжный аккаунт успешно восстановлен.",
            "Billing account has been successfully restored.",
            self.request
        )}, status=204)

    def update(self, request, *args, **kwargs):
        """
        Обновляет данные платёжного аккаунта.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на редактирование
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": translator(
                    "У вас нет прав на редактирование этого платёжного аккаунта.",
                    "You do not have the rights to edit this billing account.",
                    self.request
                )},
                status=403
            )

        # Обновление аккаунта
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class PositiveBalanceAccountsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Возвращает список платёжных аккаунтов с положительным балансом.
        Доступно только для пользователей is_staff.
        """
        if not request.user.is_staff:
            raise PermissionDenied(translator(
                "Доступ разрешён только администраторам.",
                "Access is allowed only to administrators.",
                self.request
            ))

        # Фильтруем аккаунты с положительным балансом
        accounts = PaymentAccount.objects.filter(balance__gt=0)
        serializer = PositiveBalanceAccountsSerializer(accounts, many=True)
        return Response(serializer.data)
