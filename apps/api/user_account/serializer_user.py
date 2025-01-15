from rest_framework import serializers
from .model_user import User

# Сериализатор для модели пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'referrer', 'login', 'email', 'name', 'surname', 'is_active']

# Сериализатор для регистрации
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['referrer', 'login', 'password', 'email', 'name', 'surname']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            login=validated_data['login'],
            password=validated_data['password'],
            email=validated_data['email'],
            referrer=validated_data.get('referrer', 0),
            name=validated_data.get('name', ''),
            surname=validated_data.get('surname', ''),
        )
        return user

# Сериализатор для логина
class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
