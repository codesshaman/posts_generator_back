from .token_generator import account_activation_token
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Декодирует идентификатор
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True  # Активируем аккаунт
        user.save()
        return HttpResponse("Your account has been activated successfully!")
    else:
        return HttpResponse("Activation link is invalid!")
