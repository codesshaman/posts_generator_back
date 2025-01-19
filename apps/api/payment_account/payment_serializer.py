from rest_framework import serializers
from .payment_model import PaymentAccount, Refill, Deduction

class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ['account_id', 'user_id', 'balance', 'currency', 'status', 'created_at', 'updated_at']

class RefillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refill
        fields = ['refill_id', 'account_id', 'amount', 'refill_time']

class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = ['deduction_id', 'account_id', 'amount', 'deduction_time']
