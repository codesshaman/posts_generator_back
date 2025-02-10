from apps.api.user_account.user_serializers import UserRegistrationSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from project.language import translator
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
import requests
import json


# @csrf_exempt  # Отключаем CSRF для тестов, но лучше использовать токен!
def register_user(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        vk_token = data.get("access_token")
        user_id = data.get("user_id")

        if not vk_token:
            return JsonResponse({"error": "Токен не получен"}, status=400)

        # Запрос к VK API для получения информации о пользователе
        vk_url = f"https://api.vk.com/method/users.get?user_ids={user_id}&fields=email&access_token={vk_token}&v=5.131"
        vk_response = requests.get(vk_url).json()

        if "response" in vk_response:
            user_info = vk_response["response"][0]
            return JsonResponse({
                "message": "Пользователь зарегистрирован",
                "user": user_info
            })
        else:
            return JsonResponse({"error": "Ошибка при запросе VK"}, status=400)

    return JsonResponse({"error": "Только POST запросы разрешены"}, status=405)

# def register_user(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             print(data)
#             user_id = data.get("id")
#             first_name = data.get("first_name")
#             last_name = data.get("last_name")
#             photo = data.get("photo")
#
#             if not user_id or not first_name:
#                 return JsonResponse({"error": "Неполные данные"}, status=400)
#
#             # Сохранение в базе (пример)
#             # User.objects.create(vk_id=user_id, first_name=first_name, last_name=last_name, photo=photo)
#
#             serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
#             if serializer.is_valid():
#                 serializer.save()  # Вызов метода create в сериализаторе
#                 return Response(
#                     {"message": translator(
#                         "Пользователь успешно зарегистрирован. Пожалуйста, перейдите по ссылке активации, отправленной на указанный email.",
#                         "User registered successfully. Please check your email for the activation link.",
#                         request
#                     )},
#                     status=status.HTTP_201_CREATED,
#                 )
#             # Возвращаем ошибки валидации
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#             return JsonResponse({"message": "Пользователь зарегистрирован!", "user": data})
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Некорректный JSON"}, status=400)
#
#     return JsonResponse({"error": "Метод не разрешен"}, status=405)
