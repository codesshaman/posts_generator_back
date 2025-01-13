from django.contrib import admin
from .models import New
from .models import User

@admin.register(New)
class NewAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')

# Inline для связанных моделей
class RefillInline(admin.TabularInline):
    model = User.refills.through
    extra = 1
    verbose_name = "Пополнение"
    verbose_name_plural = "Пополнения"


class DeductionInline(admin.TabularInline):
    model = User.deductions.through
    extra = 1
    verbose_name = "Списание"
    verbose_name_plural = "Списания"


class ReferralPaymentInline(admin.TabularInline):
    model = User.Referral.referral_payments.through
    extra = 1
    verbose_name = "Реферальная выплата"
    verbose_name_plural = "Реферальные выплаты"


class ReferralInline(admin.TabularInline):
    model = User.referrals.through
    extra = 1
    verbose_name = "Реферал"
    verbose_name_plural = "Рефералы"


# Основной класс для модели User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'login', 'email', 'name', 'surname', 'tariff', 'balance', 'registered_at', 'updated_at'
    )  # Поля, отображаемые в списке
    list_filter = ('tariff', 'registered_at')  # Фильтрация по полям
    search_fields = ('login', 'email', 'name', 'surname')  # Поля для поиска
    readonly_fields = ('registered_at', 'updated_at')  # Поля только для чтения
    fieldsets = (
        (None, {
            'fields': (
                'login', 'password', 'email', 'name', 'surname', 'avatar', 'tariff', 'balance', 'achievements',
                'registered_at', 'updated_at', 'api_token'
            )
        }),
        ('Связи', {
            'fields': ('referrer',)
        }),
    )
    inlines = [RefillInline, DeductionInline, ReferralInline]  # Подключение inline-моделей
