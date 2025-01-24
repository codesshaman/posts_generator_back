from apps.api.payment_account.payment_model import PaymentAccount
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .currency_model import Currency



class UserCurrenciesAPIView(APIView):
    """
    API представление для получения списка валют и их курсов, связанных с аккаунтами пользователя.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получаем текущего пользователя
        user = request.user

        # Получаем все платёжные аккаунты пользователя
        payment_accounts = PaymentAccount.objects.filter(user=user, is_active=True)

        # Извлекаем коды валют из платёжных аккаунтов
        user_currencies = payment_accounts.values_list('currency', flat=True).distinct()

        # Получаем курсы валют из таблицы Currency
        currencies = Currency.objects.filter(code__in=user_currencies)

        # Подготавливаем результат
        data = []
        for currency in currencies:
            account = payment_accounts.filter(currency=currency.code).first()
            data.append({
                'currency': currency.code,
                'rate_to_base': currency.rate,
                'payment_account_balance': account.balance if account else None
            })

        return Response(data)


class AccountCurrencyAPIView(APIView):
    """
    API представление для получения информации о валюте платёжного аккаунта по его id.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, account_id):
        # Получаем платёжный аккаунт по id
        try:
            payment_account = PaymentAccount.objects.get(pk=account_id)
        except PaymentAccount.DoesNotExist:
            raise NotFound(detail="Платёжный аккаунт не найден.")

        # Проверяем, принадлежит ли аккаунт текущему пользователю
        if payment_account.user != request.user:
            raise PermissionDenied(detail="Вы не можете просматривать этот платёжный аккаунт.")

        # Получаем валюту аккаунта
        currency_code = payment_account.currency
        try:
            currency = Currency.objects.get(code=currency_code)
        except Currency.DoesNotExist:
            raise NotFound(detail=f"Валюта с кодом {currency_code} не найдена.")

        # Формируем результат
        data = {
            'account_id': payment_account.account_id,
            'currency': currency.code,
            'rate_to_base': currency.rate,  # Убедитесь, что поле с курсом называется правильно
            'balance': payment_account.balance,
        }

        return Response(data)


class CurrencyRateAPIView(APIView):
    """
    API представление для получения курса валюты на основе её кода.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Получаем код валюты из тела запроса
        currency_code = request.data.get('currency')

        if not currency_code:
            return Response({"detail": "Поле 'currency' обязательно."}, status=400)

        # Проверяем существование валюты
        try:
            currency = Currency.objects.get(code=currency_code.upper())  # Приводим код к верхнему регистру
        except Currency.DoesNotExist:
            raise NotFound(detail=f"Валюта с кодом {currency_code} не найдена.")

        # Формируем ответ
        data = {
            'currency': currency.code,
            'rate_to_base': currency.rate  # Убедитесь, что поле с курсом называется правильно
        }

        return Response(data)