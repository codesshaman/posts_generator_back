# Generated by Django 5.1.4 on 2025-01-26 10:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_create_currency'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('plan_id', models.AutoField(primary_key=True, serialize=False)),
                ('plan', models.CharField(max_length=255, unique=True)),
                ('coins', models.DecimalField(decimal_places=6, max_digits=10)),
                ('price', models.DecimalField(decimal_places=6, max_digits=10)),
                ('monthly', models.IntegerField(blank=True, null=True)),
                ('level', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('archived_in', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('promo_id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('promo_discount', models.DecimalField(decimal_places=6, max_digits=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('archived_in', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expire_at', models.DateTimeField()),
                ('promo_expire', models.DateTimeField(blank=True, null=True)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.paymentaccount')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.plan')),
                ('promo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.promocode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
