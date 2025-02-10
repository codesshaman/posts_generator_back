from rest_framework.decorators import api_view
from rest_framework.response import Response
from project.language import translator
from rest_framework import status
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def vk_login_url(request):
    logger.debug("vk_login_url request received")
    # Проверьте, авторизован ли пользователь
    if not request.user.is_authenticated:
        logger.warning("Unauthorized access to vk_login_url")
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    auth_url = (
        f"{settings.VK_AUTH_URL}?"
        f"client_id={settings.VK_CLIENT_ID}"
        f"&display=page"
        f"&redirect_uri={settings.VK_REDIRECT_URI}"
        f"&scope=groups,wall"
        f"&response_type=code"
        f"&v={settings.VK_API_VERSION}"
    )
    return Response({"auth_url": auth_url})


# @api_view(['GET'])
# def vk_login_url(request):
#     """API для получения ссылки на авторизацию VK"""
#     auth_url = (
#         f"{settings.VK_AUTH_URL}?"
#         f"client_id={settings.VK_CLIENT_ID}"
#         f"&display=page"
#         f"&redirect_uri={settings.VK_REDIRECT_URI}"
#         f"&scope=groups,wall"
#         f"&response_type=code"
#         f"&v={settings.VK_API_VERSION}"
#     )
#     return Response({"auth_url": auth_url})


@api_view(['GET'])
def vk_callback(request):
    """API для обработки кода и получения access_token"""
    code = request.GET.get("code")
    if not code:
        return Response({"error": translator(
            "Код авторизации не найден",
            "Authorization code not found",
            request
        )}, status=status.HTTP_400_BAD_REQUEST)

    token_url = (
        f"{settings.VK_TOKEN_URL}?"
        f"client_id={settings.VK_CLIENT_ID}"
        f"&client_secret={settings.VK_CLIENT_SECRET}"
        f"&redirect_uri={settings.VK_REDIRECT_URI}"
        f"&code={code}"
    )

    response = requests.get(token_url)
    data = response.json()

    if "access_token" in data:
        return Response({
            "access_token": data["access_token"],
            "user_id": data["user_id"],
            "expires_in": data["expires_in"]
        })
    else:
        return Response({"error": data.get("error_description", translator(
            "Ошибка получения токена",
            "Token receipt error",
            request
        ))}, status=400)
