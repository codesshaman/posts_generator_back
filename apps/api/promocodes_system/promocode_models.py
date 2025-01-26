from django.db import models


class PromoCode(models.Model):
    promo_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    promo_discount = models.DecimalField(max_digits=10, decimal_places=6)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_in = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.code
