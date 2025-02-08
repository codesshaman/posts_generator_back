from django.db import models
from django.conf import settings
# from ..vk_users.vk_user_models import VkUser, VkUserToken
# from django.core.exceptions import ValidationError


class VkGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vk_groups')
    vk_id = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'vk_id')

    def __str__(self):
        return f'VK Group {self.vk_id} ({"Active" if self.is_active else "Inactive"})'
