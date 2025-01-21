from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.urls import reverse


def generate_activation_link(request, user, uid, token):
    """
    Генерирует ссылку для активации аккаунта, используя домен из запроса.
    """
    # Собираем полный URL для активации
    activation_url = reverse('activate-account', kwargs={'uidb64': uid, 'token': token})
    full_url = f"{request.scheme}://{request.get_host()}{activation_url}"
    return full_url


def send_activation_email(user, request):
    """
    Отправляет письмо для активации аккаунта.
    """
    # Генерация токена
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())  # Кодирование ID пользователя

    # Составление ссылки для активации с использованием request
    activation_link = generate_activation_link(request, user, uid, token)

    # Тема письма и его содержание
    subject = "Активируйте ваш аккаунт"
    message = f"Hi {user.login},\n\nPlease activate your account using the link below:\n{activation_link}\n\nThank you!"

    # Отправка email
    send_mail(subject, message, 'from@example.com', [user.email])
