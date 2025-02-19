# Generated by Django 5.1.4 on 2025-01-20 11:11

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_create_user_token'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAccount',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=6, default=0.0, max_digits=20)),
                ('currency', models.CharField(max_length=3)),
                ('status', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='paymentaccount',
            unique_together={('user', 'currency')},
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('deduction_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=6, max_digits=20)),
                ('deduction_time', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='api.paymentaccount')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Refill',
            fields=[
                ('refill_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=6, max_digits=20)),
                ('refill_time', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refills', to='api.paymentaccount')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
