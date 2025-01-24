from .payment_serializer import PaymentAccountSerializer, RefillSerializer, DeductionSerializer, PositiveBalanceAccountsSerializer
from .payment_model import PaymentAccount, Refill, Deduction
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


class PaymentAccountViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    """
    Представление для управления платёжными аккаунтами.
    """
    serializer_class = PaymentAccountSerializer
    permission_classes = [IsAuthenticated]

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
            raise ValidationError(f"Платёжный аккаунт с валютой {currency} уже существует для данного пользователя.")

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
    permission_classes = [IsAuthenticated]

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
            raise ValidationError(f"Платёжный аккаунт с валютой {currency} уже существует для данного пользователя.")

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
                {"detail": "У вас нет прав на удаление этого платёжного аккаунта."},
                status=403
            )

        # Мягкое удаление
        instance.is_active = False
        instance.save()

        return Response({"detail": "Платёжный аккаунт успешно деактивирован."}, status=204)


    def activate(self, request, *args, **kwargs):
        """
        Мягкое восстановление аккаунта: устанавливает is_active=True.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на восстановление
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на восстановление этого платёжного аккаунта."},
                status=403
            )

        # Мягкое восстановление
        instance.is_active = True
        instance.save()

        return Response({"detail": "Платёжный аккаунт успешно восстановлен."}, status=204)


    def update(self, request, *args, **kwargs):
        """
        Обновляет данные платёжного аккаунта.
        """
        instance = self.get_object()

        # Проверяем, имеет ли пользователь права на редактирование
        if not request.user.is_staff and instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на редактирование этого платёжного аккаунта."},
                status=403
            )

        # Обновление аккаунта
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class RefillViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    queryset = Refill.objects.all()
    serializer_class = RefillSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Создает новое пополнение и увеличивает баланс соответствующего аккаунта.
        """
        # Получаем аккаунт по account_id из запроса
        account = PaymentAccount.objects.get(account_id=self.kwargs['account_id'])
        user = self.request.user

        # Проверяем, принадлежит ли аккаунт текущему пользователю или это администратор
        if not user.is_staff and account.user != user:
            raise PermissionDenied("Вы можете проводить операции только со своими аккаунтами.")

        # Увеличиваем баланс
        account.balance += serializer.validated_data['amount']
        account.save()

        # Сохраняем объект пополнения, связанный с аккаунтом
        serializer.save(account=account)


class DeductionViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Проверяет баланс и выполняет списание, если достаточно средств.
        """
        # Получаем аккаунт
        account = PaymentAccount.objects.get(account_id=self.kwargs['account_id'])
        deduction_amount = serializer.validated_data['amount']
        user = self.request.user

        # Проверяем, принадлежит ли аккаунт текущему пользователю или это администратор
        if not user.is_staff and account.user != user:
            raise PermissionDenied("Вы можете проводить операции только со своими аккаунтами.")

        # Проверяем, достаточно ли средств на балансе
        if account.balance < deduction_amount:
            raise ValidationError(
                f"Недостаточно средств на счёте. Текущий баланс: {account.balance}, сумма списания: {deduction_amount}"
            )

        # Уменьшаем баланс
        account.balance -= deduction_amount
        account.save()

        # Сохраняем объект списания
        serializer.save(account=account)


class PositiveBalanceAccountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Возвращает список платёжных аккаунтов с положительным балансом.
        Доступно только для пользователей is_staff.
        """
        if not request.user.is_staff:
            raise PermissionDenied("Доступ разрешён только администраторам.")

        # Фильтруем аккаунты с положительным балансом
        accounts = PaymentAccount.objects.filter(balance__gt=0)
        serializer = PositiveBalanceAccountsSerializer(accounts, many=True)
        return Response(serializer.data)
