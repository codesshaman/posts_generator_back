from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .model_user import User

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('login', 'email', 'name', 'surname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('login', 'email', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'referrer')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('login', 'email')
    ordering = ('login',)

admin.site.register(User, UserAdmin)