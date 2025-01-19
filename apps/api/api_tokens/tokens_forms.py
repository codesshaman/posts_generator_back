from django.contrib import admin
from .tokens_model import UserToken


class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'get_token', 'created_at', 'expires_at', 'is_expired')
    search_fields = ['name', 'token']

    def get_token(self, obj):
        return obj.token

    get_token.short_description = 'Токен'

    def get_queryset(self, request):
        """Возвращает токены текущего пользователя или все токены."""
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset  # Для администраторов все токены
        return queryset.filter(user=request.user)  # Для обычных пользователей только их токены
