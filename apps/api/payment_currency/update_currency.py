import requests
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from .currency_model import Currency


class UpdateCurrencyRatesAPIView(APIView):
    """
    Обновление курсов валют из API.
    """
    permission_classes = [IsAdminUser]
    API_URL = "https://api.exchangerate-api.com/v4/latest/RUB"

    def get(self, request, *args, **kwargs):
        try:
            # Запрос данных с API
            response = requests.get(self.API_URL)
            response.raise_for_status()  # Проверка на успешный статус
            data = response.json()

            # Проверяем наличие курсов в ответе
            if "rates" not in data:
                return Response(
                    {"detail": "Отсутствуют курсы валют в ответе от API."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Обновление или создание записей в базе данных
            rates = data["rates"]
            for code, rate in rates.items():
                Currency.objects.update_or_create(
                    code=code,
                    defaults={
                        "rate": rate,
                        "is_active": True,  # Устанавливаем активной каждую валюту
                    },
                )

            return Response(
                {"detail": "Курсы валют успешно обновлены."},
                status=status.HTTP_200_OK,
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"detail": f"Ошибка при запросе API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"Произошла ошибка: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
