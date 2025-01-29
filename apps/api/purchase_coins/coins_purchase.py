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

        currency = data.get("currency")
        plan_name = data.get("plan")
        code = data.get("code", None)

        if not currency:
            raise ValidationError({"currency": "This field is required."}) # Это поле обязательно.
        if not plan_name:
            raise ValidationError({"plan": "This field is required."}) # Это поле обязательно.

        # Получаем тариф
        try:
            plan = Plan.objects.get(plan=plan_name, is_active=True, is_archived=False)
        except Plan.DoesNotExist:
            raise ValidationError({"plan": "The specified tariff has not been found or is inactive."}) # Указанный тариф не найден или неактивен.

        plan_price = plan.price
        promo_discount = Decimal("1.000000")

        # Проверяем промокод, если передан
        if code:
            try:
                wallet = Wallet.objects.get(user=user, is_active=True)
            except Wallet.DoesNotExist:
                raise ValidationError({"error": "User has no active wallet"}) # У пользователя нет активного кошелька.
            try:
                promo_code = PromoCode.objects.get(code=code, is_active=True, is_archived=False)
                if wallet.has_used_promo(code):
                    raise ValidationError({"promo_code": "This promocode will be used"}) # Этот промокод уже был использован.
                promo_discount = Decimal(promo_code.promo_discount)
            except PromoCode.DoesNotExist:
                pass  # Игнорируем, если промокод не найден

        # Рассчитываем итоговую стоимость
        discounted_price = (plan_price * promo_discount).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)

        with transaction.atomic():
            # 🔴 Блокируем запись платежного аккаунта
            try:
                payment_account = PaymentAccount.objects.select_for_update().get(
                    user=user, currency=currency, is_active=True
                )
            except PaymentAccount.DoesNotExist:
                raise ValidationError({"account": "The payment account with the specified currency was not found."}) # Платёжный аккаунт с указанной валютой не найден.

            if currency == "RUB":
                if payment_account.balance < discounted_price:
                    raise ValidationError({"balance": "Insufficient funds in the payment account."}) # Недостаточно средств на платёжном аккаунте.

                # Списываем средства
                payment_account.balance -= discounted_price
                payment_account.save()
            else:
                # Получаем курс валют
                try:
                    currency_rate = Currency.objects.get(code=currency, is_active=True).rate
                except Currency.DoesNotExist:
                    raise ValidationError({"currency": "The specified currency is not supported."}) # Указанная валюта не поддерживается.

                # Конвертация стоимости в рубли
                balance_in_rub = (payment_account.balance / currency_rate).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
                if balance_in_rub < discounted_price:
                    raise ValidationError({"balance": "Insufficient funds in the payment account."}) # Недостаточно средств на платёжном аккаунте.

                # Списываем средства в оригинальной валюте
                deductible_summ = (discounted_price * currency_rate).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
                payment_account.balance -= deductible_summ
                payment_account.save()

            # 🔴 Блокируем запись кошелька пользователя
            try:
                wallet = Wallet.objects.select_for_update().get(user=user, is_active=True)
            except Wallet.DoesNotExist:
                raise ValidationError({"error": "This user does not have an active wallet."}) # У пользователя нет активного кошелька.

            wallet.add_promo_code(code)
            wallet.balance += plan.coins
            wallet.save()

        return Response({
            "success": True,
            "message": "Покупка успешно завершена.",
            "coins_added": plan.coins,
            "new_wallet_balance": wallet.balance,
            "new_account_balance": payment_account.balance,
        })
