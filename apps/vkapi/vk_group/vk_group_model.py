from django.db import models
from django.conf import settings

class VkGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vk_groups')
    vk_id = models.PositiveBigIntegerField(unique=True)
    vk_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_vk_groups')
    vk_user_token = models.CharField(max_length=255, blank=True, null=True)
    vk_group_token = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'VK Group {self.vk_id} ({"Active" if self.is_active else "Inactive"})'
