from .model_token import UserToken
from django.contrib import admin


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at', 'expires_at', 'is_expired')
    search_fields = ('user__username', 'name')
    list_filter = ('created_at', 'expires_at')

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True  # Показывать как иконку (галочка или крестик) в админке
    is_expired.short_description = "Истек?"
