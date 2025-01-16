from rest_framework import serializers
from project.models import User


# Сериализатор для модели пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'login',
            'email',
            'name',
            'surname',
            'referrer',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


# Сериализатор для регистрации
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['login', 'email', 'password', 'confirm_password', 'name', 'surname']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Убираем подтверждение пароля
        return User.objects.create_user(
            login=validated_data['login'],
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            surname=validated_data.get('surname', ''),
        )


# Сериализатор для логина
class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
