from django.db import models
from django.utils.timezone import now

class User(models.Model):
    id = models.AutoField(primary_key=True)  # Уникальный идентификатор
    referrer = models.IntegerField(default=0)  # Пригласитель (по умолчанию root)
    registered_at = models.DateTimeField(default=now)  # Дата регистрации
    updated_at = models.DateTimeField(default=now)  # Дата обновления
    login = models.CharField(max_length=150, unique=True)  # Уникальный никнейм
    password = models.CharField(max_length=128)  # md5 хэш пароля
    email = models.EmailField(unique=True)  # Почта
    name = models.CharField(max_length=100)  # Имя
    surname = models.CharField(max_length=100)  # Фамилия

    # Выбор аватара
    AVATAR_CHOICES = [
        ('avatar1', 'Avatar 1'),
        ('avatar2', 'Avatar 2'),
        ('avatar3', 'Avatar 3'),
    ]
    avatar = models.CharField(max_length=50, choices=AVATAR_CHOICES)

    # Тариф
    TARIFF_CHOICES = [
        (0, 'Free'),
        (1, 'Basic'),
        (2, 'Premium'),
    ]
    tariff = models.IntegerField(choices=TARIFF_CHOICES, default=0)

    balance = models.IntegerField(default=0)  # Баланс

    # Список достижений
    class Achievement(models.TextChoices):
        ACHIEVEMENT_1 = 'ach1', 'Achievement 1'
        ACHIEVEMENT_2 = 'ach2', 'Achievement 2'
        ACHIEVEMENT_3 = 'ach3', 'Achievement 3'

    achievements = models.JSONField(default=list, blank=True)  # Список достижений (JSON)

    # Пополнения
    class Refill(models.Model):
        refill_datetime = models.DateTimeField(default=now)  # Дата пополнения
        refill_amount = models.IntegerField()  # Сумма пополнения

    refills = models.ManyToManyField(Refill, blank=True)  # Связь с пополнениями

    # Списания
    class Deduction(models.Model):
        deduction_datetime = models.DateTimeField(default=now)  # Дата списания
        deduction_amount = models.IntegerField()  # Сумма списания
        model = models.CharField(max_length=100)  # Модель
        content = models.CharField(max_length=100)  # Тип контента
        content_size = models.CharField(max_length=100)  # Размер контента

    deductions = models.ManyToManyField(Deduction, blank=True)  # Связь со списаниями

    api_token = models.CharField(max_length=128, unique=True, blank=True, null=True)  # API-токен

    # Приглашённые (рефералы)
    class Referral(models.Model):
        referral_id = models.IntegerField()  # ID приглашённого
        referral_level = models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')])  # Уровень реферала

        # Реферальные выплаты
        class ReferralPayment(models.Model):
            payment_datetime = models.DateTimeField(default=now)  # Дата выплаты
            payment_amount = models.IntegerField()  # Сумма выплаты

        referral_payments = models.ManyToManyField(ReferralPayment, blank=True)  # Связь с выплатами

    referrals = models.ManyToManyField(Referral, blank=True)  # Связь с рефералами
