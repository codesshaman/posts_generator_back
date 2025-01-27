from ..user_wallet.wallet_models import Wallet
from django.utils import timezone
from django.db import models

class WalletDeduction(models.Model):
    deduction_id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="deductions")
    amount = models.DecimalField(max_digits=20, decimal_places=6)
    deduction_time = models.DateTimeField(default=timezone.now, editable=False)  # Не редактируемое поле
    is_active = models.BooleanField(default=True)  # Поле для мягкого удаления

    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление"""
        self.is_active = False
        self.save()

    def restore(self):
        """Восстановление удалённой записи"""
        self.is_active = True
        self.save()

    def __str__(self):
        return f"Deduction {self.deduction_id} for wallet {self.wallet.wallet_id} of amount {self.amount}"
