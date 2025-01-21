from .payment_serializer import PaymentAccountSerializer, RefillSerializer, DeductionSerializer, PositiveBalanceAccountsSerializer
from .payment_model import PaymentAccount, Refill, Deduction
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.views import APIView


class PaymentAccountViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = PaymentAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только платёжные аккаунты текущего авторизованного пользователя.
        """
        return PaymentAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        # Проверяем, существует ли уже платёжный аккаунт для пользователя
        if PaymentAccount.objects.filter(user=user).exists():
            raise ValidationError("Платёжный аккаунт для данного пользователя уже существует.")

        # Создаем новый платёжный аккаунт
        serializer.save(user_id=user.id)

    @action(detail=True, methods=['get'])
    def refills(self, request, pk=None):
        """
        Возвращает список пополнений для указанного платёжного аккаунта.
        """
        account = self.get_object()
        refills = account.refills.all()
        serializer = RefillSerializer(refills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def deductions(self, request, pk=None):
        """
        Возвращает список списаний для указанного платёжного аккаунта.
        """
        account = self.get_object()
        deductions = account.deductions.all()
        serializer = DeductionSerializer(deductions, many=True)
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
