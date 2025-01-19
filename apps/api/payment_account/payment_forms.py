from django import forms
from .payment_model import PaymentAccount, Refill, Deduction

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
