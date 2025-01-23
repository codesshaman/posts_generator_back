from rest_framework import serializers
from .payment_model import PaymentAccount, Refill, Deduction

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

class RefillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refill
        fields = ['refill_id', 'account_id', 'amount', 'refill_time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and not request.user.is_staff:
            # Получаем пользователя через связанный аккаунт
            account_user = instance.account.user
            if account_user != request.user:
                representation.pop('amount')  # Скрываем сумму пополнения
        return representation

class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = ['deduction_id', 'account_id', 'amount', 'deduction_time']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and not request.user.is_staff:
            # Получаем пользователя через связанный аккаунт
            account_user = instance.account.user
            if account_user != request.user:
                representation.pop('amount')  # Скрываем сумму пополнения
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