from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from project.language import translator
from django.http import HttpResponse


User = get_user_model()

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    pass

account_activation_token = AccountActivationTokenGenerator()


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Декодирует идентификатор
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True  # Активируем аккаунт
        user.save()
        return HttpResponse(translator(
            "Ваша учетная запись успешно активирована!",
            "Your account has been activated successfully!",
            request
        ))
    else:
        return HttpResponse(translator(
            "Ссылка для активации недействительна!",
            "Activation link is invalid!",
            request
        ))
