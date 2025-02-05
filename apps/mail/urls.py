from .password_restore.user_password_restore_view import *
from .views import activate_account
from django.urls import path


urlpatterns = [
    # Активация аккаунта
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    # Восстановление утерянного пароля
    path('password-reset/', RequestPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/', ConfirmPasswordResetView.as_view(), name='password_reset_confirm'),
]