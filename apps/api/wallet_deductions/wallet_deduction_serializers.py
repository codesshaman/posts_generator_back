from .wallet_deduction_models import WalletDeduction
from rest_framework import serializers


class WalletDeductionSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.DecimalField(
        max_digits=20, decimal_places=6, read_only=True
    )  # Поле для баланса кошелька
    current_balance = serializers.DecimalField(
        max_digits=20, decimal_places=6, read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)  # Только для чтения
    wallet = serializers.PrimaryKeyRelatedField(read_only=True)  # wallet_id только для чтения

    class Meta:
        model = WalletDeduction
        fields = ['deduction_id', 'wallet', 'amount', 'deduction_time', 'current_balance', 'is_active', 'wallet_balance']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Получаем баланс связанного кошелька
        representation['wallet_balance'] = instance.wallet.balance if instance.wallet else None

        # Скрываем сумму списания для обычных пользователей
        if request and not request.user.is_staff:
            wallet_user = instance.wallet.user
            if wallet_user != request.user:
                representation.pop('amount')  # Скрываем сумму списания
        return representation
