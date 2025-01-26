from django import forms
from .payment_model import PaymentAccount
from ..payment_account_refill.refill_model import Refill
from ..payment_account_deduction.deduction_model import Deduction

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
