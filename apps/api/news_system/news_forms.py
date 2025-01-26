from django.contrib import admin
from .news_models import New


@admin.register(New)
class NewAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
