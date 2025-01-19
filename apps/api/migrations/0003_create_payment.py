# Generated by Django 5.1.4 on 2025-01-19 17:17

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_create_token'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAccount',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('balance', models.IntegerField()),
                ('currency', models.CharField(max_length=3)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('deduction_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('deduction_time', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='api.paymentaccount')),
            ],
        ),
        migrations.CreateModel(
            name='Refill',
            fields=[
                ('refill_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('refill_time', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refills', to='api.paymentaccount')),
            ],
        ),
    ]
