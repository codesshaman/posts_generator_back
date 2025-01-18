from rest_framework import serializers
from django.utils.timezone import now, timedelta
from .tokens_model import UserToken

class UserTokenSerializer(serializers.ModelSerializer):
    expires_in_days = serializers.IntegerField(
        write_only=True, required=False, min_value=1, max_value=365,
        help_text="Время жизни токена в днях (по умолчанию 30)"
    )

    class Meta:
        model = UserToken
        fields = ['id', 'name', 'token', 'created_at', 'expires_at', 'expires_in_days']
        read_only_fields = ['id', 'token', 'created_at', 'expires_at']

    def create(self, validated_data):
        user = self.context['request'].user
        expires_in_days = validated_data.pop('expires_in_days', 30)  # По умолчанию 30 дней
        expires_at = now() + timedelta(days=expires_in_days)
        validated_data['expires_at'] = expires_at
        validated_data['user'] = user

        # Генерация токена (пример: UUID)
        from uuid import uuid4
        validated_data['token'] = str(uuid4())

        return super().create(validated_data)
