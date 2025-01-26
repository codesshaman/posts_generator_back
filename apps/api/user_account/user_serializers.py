from apps.mail.acc_activation.activation_mail_sendler import send_activation_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import serializers
User = get_user_model()

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
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['login', 'email', 'name', 'surname', 'referrer', 'password', 'password_confirm']

    def validate(self, data):
        # Проверка совпадения паролей
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')  # Удаляем поле подтверждения пароля
        try:
            user = User.objects.create_user(
                login=validated_data['login'],
                email=validated_data['email'],
                name=validated_data.get('name', ''),
                surname=validated_data.get('surname', ''),
                referrer=validated_data.get('referrer', None),
                password=validated_data['password']
            )
            # Отправка письма с активацией
            send_activation_email(user, self.context['request'])

            return user

        except ValidationError as e:
            raise serializers.ValidationError({'detail': str(e)})
        except Exception as e:
            raise serializers.ValidationError({'detail': "An unexpected error occurred: " + str(e)})

# Сериализатор для логина
class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
