from django.conf import settings
from django.db import models


class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=6, default=0.000000)
    status = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'wallet_id')

    def __str__(self):
        return f"Wallet {self.wallet_id} for user {self.user}"
