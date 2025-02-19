from apps.mail.acc_activation.activation_mail_sendler import send_activation_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import serializers
User = get_user_model()


# Сериализатор для регистрации
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['login', 'email', 'auth', 'name', 'surname', 'referrer', 'password', 'password_confirm']

    def validate(self, data):
        # Проверка совпадения паролей
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')  # Удаляем поле подтверждения пароля
        if validated_data.get('auth') != 'email':
            validated_data['email'] = None
        try:
            user = User.objects.create_user(
                login=validated_data['login'],
                email=validated_data['email'],
                auth=validated_data['auth'],
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


# Сериализатор для модели пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['login', 'email', 'vk', 'auth', 'name', 'surname', 'referrer']

    def validate(self, data):
        auth_method = data.get('auth')

        if auth_method == 'email':
            if not data.get('email'):
                raise serializers.ValidationError("Поле email обязательно для метода аутентификации email.")

        elif auth_method == 'vk':
            if not data.get('vk'):
                raise serializers.ValidationError("Поле vk обязательно для метода аутентификации VK.")

        elif auth_method == 'google':
            if 'request' in self.context and hasattr(self.context['request'], 'user_data'):
                google_data = self.context['request'].user_data
                data['email'] = google_data.get('email')
            else:
                raise serializers.ValidationError("Не удалось получить email из Google.")

        return data

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        if user.auth == 'email':
            user.is_active = False  # Требуется активация
            # Отправка письма с подтверждением (реализуйте отдельно)
        else:
            user.is_active = True  # VK и Google сразу активны

        user.set_password(validated_data.get('password', 'defaultpassword'))
        user.save()
        return user


# Сериализатор для логина
class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)
