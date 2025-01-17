from django.db import models
from django.contrib.auth.models import User  # Используем стандартную модель пользователя
from django.utils.timezone import now, timedelta


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    name = models.CharField(max_length=255, verbose_name="Название токена")
    token = models.TextField(verbose_name="Токен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    expires_at = models.DateTimeField(verbose_name="Дата истечения", null=True, blank=True)

    class Meta:
        verbose_name = "Токен пользователя"
        verbose_name_plural = "Токены пользователей"
        unique_together = ('user', 'name')  # Пользователь не может иметь два токена с одинаковым названием
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def is_expired(self):
        """Проверка истек ли токен."""
        if self.expires_at:
            return now() > self.expires_at
        return False

    def extend_expiration(self, days=30):
        """Продление времени истечения токена."""
        self.expires_at = now() + timedelta(days=days)
        self.save()
