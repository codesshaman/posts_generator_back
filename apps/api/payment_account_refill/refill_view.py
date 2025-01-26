from apps.api.payment_account.payment_model import PaymentAccount
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .refill_serializer import RefillSerializer
from rest_framework import viewsets, mixins
from .refill_model import Refill


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
