from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .api_tokens.tokens_models import UserToken


class ZUserTokenPermission(BasePermission):
    def has_permission(self, request, view):
        jwt_authenticator = JWTAuthentication()
        user = None

        # 1️⃣ Проверяем JWT в Authorization
        jwt_token = request.headers.get("Authorization")
        if jwt_token:
            try:
                user, token = jwt_authenticator.authenticate(request)
                if user:
                    if not user.is_active:
                        raise AuthenticationFailed("User account is inactive.")

                    request.user = user
                    request.auth = token
                    return True
            except AuthenticationFailed as e:
                raise AuthenticationFailed(f"🚫 JWT недействителен: {str(e)}")

        # 2️⃣ Проверяем Z-User-Tokens
        token_value = request.headers.get("Z-User-Token")

        if token_value:
            try:
                user_token = UserToken.objects.get(token=token_value)

                if user_token.is_expired:
                    raise AuthenticationFailed("Token has expired")

                user = user_token.user
                if not user.is_active:
                    raise AuthenticationFailed("User account is inactive.")

                request.user = user
                request.auth = user_token
                return True
            except UserToken.DoesNotExist:
                raise AuthenticationFailed("Invalid token")

        raise AuthenticationFailed("Authentication credentials were not provided or are invalid")
