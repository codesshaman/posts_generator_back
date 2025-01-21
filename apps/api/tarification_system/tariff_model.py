from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan = models.CharField(max_length=255, unique=True)
    ratio = models.DecimalField(max_digits=10, decimal_places=6)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_in = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.plan


class PromoCode(models.Model):
    promo_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    promo_ratio = models.DecimalField(max_digits=10, decimal_places=6)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_in = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.code


class UserPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey('api.PaymentAccount', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    expire_at = models.DateTimeField()
    promo = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True)
    promo_expire = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.plan.plan}"
