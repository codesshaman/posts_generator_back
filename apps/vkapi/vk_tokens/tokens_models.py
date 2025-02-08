from django.conf import settings
from django.db import models


class VKToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем кастомную модель пользователя
        on_delete=models.CASCADE,
        related_name="vk_tokens"
    )
    name = models.CharField(max_length=255, verbose_name="Название токена")
    token = models.TextField(verbose_name="Токен ВК")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Токен вконтакте"
        verbose_name_plural = "Токены вконтакте"
        unique_together = ('user', 'token')  # Пользователь не может иметь два одинаковых токена
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"
