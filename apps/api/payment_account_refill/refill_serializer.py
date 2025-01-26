from rest_framework import serializers
from .refill_model import Refill


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
