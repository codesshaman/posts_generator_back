import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VkGroup',
            fields=[
                ('group_id', models.AutoField(primary_key=True, serialize=False)),
                ('vk_id', models.PositiveBigIntegerField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vk_groups',
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'vk_id')},
            },
        ),
        migrations.CreateModel(
            name='VKToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название токена')),
                ('token', models.TextField(verbose_name='Токен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vk_tokens',
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Токен vk',
                'verbose_name_plural': 'Токены вконтакте',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'name')},
            },
        ),
    ]
