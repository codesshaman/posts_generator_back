from django.contrib import admin
from .news_system.news_admin import NewAdmin
from .user_account.user_admin import UserAdmin
from .api_tokens.tokens_admin import UserTokenAdmin
# from project.models import User
#
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('login', 'email', 'is_active', 'is_staff')
#     search_fields = ('login', 'email')
#     list_filter = ('is_staff', 'is_active')
