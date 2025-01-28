from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from ..user_wallet.wallet_models import Wallet
from ..payment_account.payment_models import PaymentAccount
from ..payment_currency.currency_models import Currency
from ..tariffication_system.tariff_models import Plan
from ..promocodes_system.promocode_models import PromoCode


class CoinPurchaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Получение данных из запроса
        code = data.get("code")  # Промокод (необязательное поле)
        currency = data.get("currency")  # Валюта (обязательное поле)
        plan_name = data.get("plan")  # Тариф (обязательное поле)

        if not currency:
            raise ValidationError({"currency": "Это поле обязательно."})
        if not plan_name:
            raise ValidationError({"plan": "Это поле обязательно."})

        # Получение тарифа
        try:
            plan = Plan.objects.get(plan=plan_name, is_active=True, is_archived=False)
        except Plan.DoesNotExist:
            raise ValidationError({"plan": "Указанный тариф не найден или неактивен."})

        plan_price = plan.price
        promo_discount = 1.000000

        # Применение промокода, если указан
        if code:
            try:
                promo_code = PromoCode.objects.get(code=code, is_active=True, is_archived=False)
                promo_discount = promo_code.promo_discount
            except PromoCode.DoesNotExist:
                pass  # Промокод не найден, скидка не применяется

        # Получение платёжного аккаунта
        try:
            payment_account = PaymentAccount.objects.get(user=user, currency=currency, is_active=True)
        except PaymentAccount.DoesNotExist:
            raise ValidationError({"account": "Платёжный аккаунт с указанной валютой не найден."})

        # Приведение promo_discount к Decimal
        promo_discount = Decimal(promo_discount)
        # Расчёт итоговой стоимости тарифа с учётом скидки
        discounted_price = (plan_price * promo_discount).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
        # Для валюты RUB
        if currency == "RUB":
            if payment_account.balance < discounted_price:
                raise ValidationError({"balance": "Недостаточно средств на платёжном аккаунте."})

            # Выполнение транзакции
            with transaction.atomic():
                payment_account.balance -= discounted_price
                payment_account.save()

                try:
                    wallet = Wallet.objects.get(user=user, is_active=True)
                except Wallet.DoesNotExist:
                    return Response(
                        {"error": "У пользователя нет активного кошелька."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                wallet.balance += plan.coins
                wallet.save()

        else:
            # Для других валют
            try:
                currency_rate = Currency.objects.get(code=currency, is_active=True).rate
            except Currency.DoesNotExist:
                raise ValidationError({"currency": "Указанная валюта не поддерживается."})
            # Конвертация стоимости в рубли
            # balance_in_rub = payment_account.balance * currency_rate
            balance_in_rub = (payment_account.balance / currency_rate).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
            if balance_in_rub < discounted_price:
                raise ValidationError({"balance": "Недостаточно средств на платёжном аккаунте (с учётом курса валют)."})

            # Выполнение транзакции
            with transaction.atomic():
                deductible_summ = (discounted_price * currency_rate).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
                payment_account.balance -= deductible_summ
                payment_account.save()

                try:
                    wallet = Wallet.objects.get(user=user, is_active=True)
                except Wallet.DoesNotExist:
                    return Response(
                        {"error": "У пользователя нет активного кошелька."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                wallet.balance += plan.coins
                wallet.save()

        return Response({
            "success": True,
            "message": "Покупка успешно завершена.",
            "coins_added": plan.coins,
            "new_wallet_balance": wallet.balance,
            "new_account_balance": payment_account.balance,
        })
