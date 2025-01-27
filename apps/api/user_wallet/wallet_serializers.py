from rest_framework import serializers
from .wallet_models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_id', 'user_id', 'balance', 'status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Скрываем информацию о балансе для других пользователей, если это не администратор.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and not request.user.is_staff and instance.user != request.user:
            representation.pop('balance')  # Скрываем баланс
        return representation

class PositiveBalanceWalletsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_id', 'user_id', 'balance', 'status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Скрываем информацию о балансе для других пользователей, если это не администратор.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and not request.user.is_staff and instance.user != request.user:
            representation.pop('balance')  # Скрываем баланс
        return representation