from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from ..permissions import ZUserTokenPermission
from project.language import translator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..user_wallet.wallet_models import Wallet
from ..payment_account.payment_models import PaymentAccount
from ..payment_currency.currency_models import Currency
from ..tariffication_system.tariff_models import Plan
from ..promocodes_system.promocode_models import PromoCode


class CoinPurchaseAPIView(APIView):
    permission_classes = [ZUserTokenPermission]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        currency = data.get("currency")
        plan_name = data.get("plan")
        code = data.get("code", None)

        if not currency:
            raise ValidationError({"currency": translator(
                "Это поле обязательно.",
                "This field is required.",
                self.request
            )}) #
        if not plan_name:
            raise ValidationError({"plan": translator(
                "Это поле обязательно.",
                "This field is required.",
                self.request
            )}) #

        # Получаем тариф
        try:
            plan = Plan.objects.get(plan=plan_name, is_active=True, is_archived=False)
        except Plan.DoesNotExist:
            raise ValidationError({"plan": translator(
                "Указанный тариф не найден или неактивен.",
                "The specified plan has not been found or is inactive.",
                self.request
            )})

        plan_price = plan.price
        promo_discount = Decimal("1.000000")

        # Проверяем промокод, если передан
        if code:
            try:
                wallet = Wallet.objects.get(user=user, is_active=True)
            except Wallet.DoesNotExist:
                raise ValidationError({"error": translator(
                    "У пользователя нет активного кошелька.",
                    "The user does not have an active wallet.",
                    self.request
                )})
            try:
                promo_code = PromoCode.objects.get(code=code, is_active=True, is_archived=False)
                if wallet.has_used_promo(code):
                    raise ValidationError({"promo_code": translator(
                        "Этот промокод уже был использован.",
                        "This promo code has already been used.",
                        self.request
                    )})
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
                raise ValidationError({"account": translator(
                    "Платёжный аккаунт с указанной валютой не найден.",
                    "The billing account with the specified currency was not found.",
                    self.request
                )})

            if currency == "RUB":
                if payment_account.balance < discounted_price:
                    raise ValidationError({"balance": translator(
                        "Недостаточно средств на платёжном аккаунте.",
                        "Insufficient funds in the billing account.",
                        self.request
                    )})

                # Списываем средства
                payment_account.balance -= discounted_price
                payment_account.save()
            else:
                # Получаем курс валют
                try:
                    currency_rate = Currency.objects.get(code=currency, is_active=True).rate
                except Currency.DoesNotExist:
                    raise ValidationError({"currency": translator(
                        "Указанная валюта не поддерживается.",
                        "The specified currency is not supported.",
                        self.request
                    )})

                # Конвертация стоимости в рубли
                balance_in_rub = (payment_account.balance / currency_rate).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
                if balance_in_rub < discounted_price:
                    raise ValidationError({"balance": translator(
                        "Недостаточно средств на платёжном аккаунте.",
                        "Insufficient funds in the billing account.",
                        self.request
                    )})

                # Списываем средства в оригинальной валюте
                deductible_summ = (discounted_price * currency_rate).quantize(Decimal("0.000000"), rounding=ROUND_DOWN)
                payment_account.balance -= deductible_summ
                payment_account.save()

            # 🔴 Блокируем запись кошелька пользователя
            try:
                wallet = Wallet.objects.select_for_update().get(user=user, is_active=True)
            except Wallet.DoesNotExist:
                raise ValidationError({"error": translator(
                    "У пользователя нет активного кошелька.",
                    "The user does not have an active wallet.",
                    self.request
                )})

            wallet.add_promo_code(code)
            wallet.balance += plan.coins
            wallet.save()

        return Response({
            "success": True,
            "message": translator(
                "Покупка успешно завершена.",
                "The purchase has been successfully completed.",
                self.request
            ),
            "coins_added": plan.coins,
            "new_wallet_balance": wallet.balance,
            "new_account_balance": payment_account.balance,
        })
