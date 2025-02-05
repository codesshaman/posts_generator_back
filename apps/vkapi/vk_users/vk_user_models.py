from django.db import models
from ..vk_groups.vk_group_models import VkGroup


class VkUser(models.Model):
    record_id = models.AutoField(primary_key=True)
    vk_id = models.PositiveBigIntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    profile_url = models.URLField(blank=True, null=True)
    groups = models.ForeignKey(VkGroup, on_delete=models.CASCADE, related_name='vk_users')

    def __str__(self):
        return f'{self.first_name} {self.last_name} (ID: {self.vk_id})'

class VkUserToken(models.Model):
    user = models.ForeignKey(VkUser, on_delete=models.CASCADE, related_name='user_tokens')
    token = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Token for {self.user}'
