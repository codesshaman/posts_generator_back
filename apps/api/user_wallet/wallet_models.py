from django.db import models
from django.conf import settings

class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=6, default=0.000000)
    status = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    promo_codes = models.JSONField(default=list)  # Хранение списка использованных промокодов
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_promo_code(self, code):
        """Добавляет промокод в список использованных, если он ещё не применялся."""
        if code not in self.promo_codes:
            self.promo_codes.append(code)
            self.save(update_fields=['promo_codes'])

    def has_used_promo(self, code):
        """Проверяет, использовал ли пользователь данный промокод."""
        return code in self.promo_codes

    class Meta:
        unique_together = ('user', 'wallet_id')

    def __str__(self):
        return f"Wallet {self.wallet_id} for user {self.user}"
