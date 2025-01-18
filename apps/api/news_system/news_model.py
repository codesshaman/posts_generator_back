from django.db import models


class New(models.Model):
    title = models.CharField(max_length=255)  # Заголовок
    description = models.TextField()         # Описание
    image_url = models.URLField(blank=True, null=True)  # Ссылка на изображение
    content = models.TextField()             # Текст новости
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)      # Дата изменения

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
