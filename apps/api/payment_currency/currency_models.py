from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # ISO-код валюты, например USD, EUR, UAH
    name = models.CharField(max_length=50)  # Название валюты
    rate = models.DecimalField(max_digits=15, decimal_places=6)  # Курс валюты относительно базовой
    is_active = models.BooleanField(default=True)  # Учитывать ли валюту
    updated_at = models.DateTimeField(auto_now=True)  # Время последнего обновления курса

    def __str__(self):
        return f"{self.code} ({self.rate})"
