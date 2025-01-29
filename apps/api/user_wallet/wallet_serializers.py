from rest_framework import serializers
from .wallet_models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_id', 'user_id', 'balance', 'status', 'promo_codes', 'created_at', 'updated_at']
        extra_kwargs = {
            'balance': {'read_only': True},  # Поле только для чтения
            'promo_codes': {'read_only': True}  # Запрещаем изменение списка промокодов через API
        }

    def to_representation(self, instance):
        """
        Убираем пустые строки из списка промокодов.
        Скрываем баланс и промокоды для других пользователей, если это не администратор.
        """
        representation = super().to_representation(instance)
        representation['promo_codes'] = [code for code in representation.get('promo_codes', []) if code.strip()]

        request = self.context.get('request')
        if request and not request.user.is_staff and instance.user != request.user:
            representation.pop('balance', None)
            representation.pop('promo_codes', None)  # Скрываем список использованных промокодов
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
