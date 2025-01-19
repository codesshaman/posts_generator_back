from django.utils import timezone
from django.conf import settings
from django.db import models


class PaymentAccount(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.IntegerField()
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment account {self.account_id} for user {self.user}"

class Refill(models.Model):
    refill_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(PaymentAccount, on_delete=models.CASCADE, related_name="refills")
    amount = models.IntegerField()
    refill_time = models.DateTimeField(default=timezone.now, editable=False)  # Не редактируемое поле

    def __str__(self):
        return f"Refill {self.refill_id} for account {self.account.account_id} of amount {self.amount}"

class Deduction(models.Model):
    deduction_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(PaymentAccount, on_delete=models.CASCADE, related_name="deductions")
    amount = models.IntegerField()
    deduction_time = models.DateTimeField(default=timezone.now, editable=False)  # Не редактируемое поле

    def __str__(self):
        return f"Deduction {self.deduction_id} for account {self.account.account_id} of amount {self.amount}"
