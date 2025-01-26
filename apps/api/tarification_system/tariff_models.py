from ..promocodes_system.promocode_models import PromoCode
from rest_framework import serializers
from django.conf import settings
from django.db import models


class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan = models.CharField(max_length=255, unique=True)
    coins = models.DecimalField(max_digits=10, decimal_places=6)
    price = models.DecimalField(max_digits=10, decimal_places=6)
    monthly = models.IntegerField(null=True, blank=True)
    level = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_in = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.plan


class UserPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey('api.PaymentAccount', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    expire_at = models.DateTimeField()
    promo = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True)
    promo_expire = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.plan.plan}"
