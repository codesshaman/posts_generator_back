from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from apps.api.permissions import ZUserTokenPermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from project.language import translator
from project.language import fs_translator
from rest_framework.permissions import AllowAny

User = get_user_model()


class RequestPasswordResetView(APIView):
    """Запрос на сброс пароля (отправка письма)"""
    permission_classes = [AllowAny, ZUserTokenPermission]

    def post(self, request):
        identifier = request.data.get("identifier")  # Либо email, либо login

        if not identifier:
            return Response({"error": translator(
                "Требуется логин или адрес электронной почты",
                "Login or email is required",
                self.request
            )}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "@" in identifier:  # Если введен email
                user = User.objects.get(email=identifier)
            else:  # Если введен login
                user = User.objects.get(login=identifier)

            email = user.email
        except User.DoesNotExist:
            return Response({"error": translator(
                "Пользователь не найден",
                "User not found",
                self.request
            )}, status=status.HTTP_404_NOT_FOUND)

        # Генерация токена
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"https://your-frontend.com/password-reset/{uid}/{token}"

        subject = translator(
            "Запрос на восстановление пароля",
            "Password Reset Request",
            self.request
        )

        message = fs_translator(
            self.request,
            "Здравствуйте, {0}!\n\nПерейдите по ссылке для восстановления пароля:\n{1}",
            "Hi {0}!\n\nClick the link below to reset your password:\n{1}",
            user.login, reset_link
        )
        # Отправка письма
        send_mail(
            subject,
            message,
            "no-reply@yourdomain.com",
            [email],
            fail_silently=False,
        )

        # # Отправка письма
        # send_mail(
        #     "Password Reset Request",
        #     f"Hi {user.login},\n\nClick the link below to reset your password:\n{reset_link}",
        #     "no-reply@yourdomain.com",
        #     [email],
        #     fail_silently=False,
        # )

        return Response({"message": translator(
            "Вам отправлена ссылка для сброса пароля",
            "Password reset link sent",
            self.request
        )}, status=status.HTTP_200_OK)


class ConfirmPasswordResetView(APIView):
    """Подтверждение сброса пароля"""
    permission_classes = [AllowAny, ZUserTokenPermission]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not uid or not token or not new_password:
            return Response({"error": translator(
                "Недостающие параметры",
                "Missing parameters",
            )}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": translator(
                "Токен недействителен!",
                "Invalid token!",
            self.request
            )}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": translator(
                "Недействительный или просроченный токен",
                "Invalid or expired token",
                self.request
            )}, status=status.HTTP_400_BAD_REQUEST)

        # Обновление пароля
        user.set_password(new_password)
        user.save()

        return Response({"message": translator(
            "Сброс пароля прошёл успешно",
            "Password reset successful",
            self.request
        )}, status=status.HTTP_200_OK)
