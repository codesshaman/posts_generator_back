from rest_framework import serializers
from .payment_models import PaymentAccount

class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ['account_id', 'user_id', 'balance', 'currency', 'status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Скрываем информацию о балансе для других пользователей, если это не администратор.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and not request.user.is_staff and instance.user != request.user:
            representation.pop('balance')  # Скрываем баланс
        return representation

class PositiveBalanceAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ['account_id', 'user_id', 'balance', 'currency', 'status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Скрываем информацию о балансе для других пользователей, если это не администратор.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and not request.user.is_staff and instance.user != request.user:
            representation.pop('balance')  # Скрываем баланс
        return representation