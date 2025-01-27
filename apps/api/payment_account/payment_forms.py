from django import forms
from .payment_models import PaymentAccount
from ..payment_account_refills.refill_models import Refill
from ..payment_account_deductions.deduction_models import Deduction

class PaymentAccountForm(forms.ModelForm):
    class Meta:
        model = PaymentAccount
        fields = ['user', 'balance', 'currency', 'status']

class RefillForm(forms.ModelForm):
    class Meta:
        model = Refill
        fields = ['account', 'amount']

class DeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['account', 'amount']
