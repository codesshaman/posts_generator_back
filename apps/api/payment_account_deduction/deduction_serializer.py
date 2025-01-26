from rest_framework import serializers
from .deduction_model import Deduction


class DeductionSerializer(serializers.ModelSerializer):
    account_balance = serializers.DecimalField(
        max_digits=20, decimal_places=6, read_only=True
    )  # Поле для баланса аккаунта
    current_balance = serializers.DecimalField(
        max_digits=20, decimal_places=6, read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)  # Только для чтения
    account = serializers.PrimaryKeyRelatedField(read_only=True)  # account_id только для чтения

    class Meta:
        model = Deduction
        fields = ['deduction_id', 'account', 'amount', 'deduction_time', 'current_balance', 'is_active', 'account_balance']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Получаем баланс связанного аккаунта
        representation['account_balance'] = instance.account.balance if instance.account else None

        # Скрываем сумму списания для обычных пользователей
        if request and not request.user.is_staff:
            account_user = instance.account.user
            if account_user != request.user:
                representation.pop('amount')  # Скрываем сумму списания
        return representation

