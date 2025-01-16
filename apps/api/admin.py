from django.contrib import admin
from .news_system.admin_news import NewAdmin
from .user_account.admin_user import UserAdmin
# from project.models import User
#
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('login', 'email', 'is_active', 'is_staff')
#     search_fields = ('login', 'email')
#     list_filter = ('is_staff', 'is_active')
