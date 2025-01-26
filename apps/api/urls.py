from .payment_account.payment_views import PaymentAccountViewSet, PaymentAccountsViewSet, PositiveBalanceAccountsView
from .payment_account_deduction.deduction_view import DeductionViewSet
from .payment_account_refill.refill_view import RefillViewSet
from .user_account.user_views import UserViewSet, UserRegistrationAPIView
from .api_tokens.tokens_views import UserTokenViewSet
from .payment_currency.update_currency import UpdateCurrencyRatesAPIView
from .payment_currency.currency_view import UserCurrenciesAPIView, AccountCurrencyAPIView, CurrencyRateAPIView
from .tarification_system.tariff_views import PlanViewSet, PromoCodeViewSet, UserPlanViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .news_system.news_views import NewViewSet
from apps.mail.acc_activation.activation_view import activate_account
from rest_framework.routers import DefaultRouter
from django.urls import path, include


# Роутер для автоматического создания маршрутов
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),  # Подключение всех маршрутов из роутера

    # Регистрация нового пользователя POST: {{url}}/api/register/
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),

    # Активация аккаунта по email
    path('activate/<str:uidb64>/<str:token>/', activate_account, name='activate-account'),

    # # Маршруты для получения / обновления JWT-токенов POST:{{url}}/api/token/
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Маршруты для новостей
    path('news/', NewViewSet.as_view({
        'get': 'list',              # GET : {{url}}/api/news/
        'post': 'create'            # POST: {{url}}/api/news/
    }), name='news-list-create'),
    path('news/<int:pk>/', NewViewSet.as_view({
        'get': 'retrieve',          # GET :  {{url}}/api/news/<new_id>/
        'put': 'update',            # PUT :  {{url}}/api/news/<new_id>/
        'patch': 'partial_update',  # PATCH :{{url}}/api/news/<new_id>/
        'delete': 'destroy'         # DELETE:{{url}}/api/news/<new_id>/
    }), name='news-detail'),

    # Платёжные аккаунты
    path('payments/', PaymentAccountViewSet.as_view({
        'get': 'list',              # GET : {{url}}/api/payments/
        'post': 'create'            # POST: {{url}}/api/payments/
    }), name='payment_account-list'),
    path('payments/<int:pk>/', PaymentAccountsViewSet.as_view({
        'get': 'retrieve',          # GET :  {{url}}/api/payments/<acc_id>/
        'delete': 'destroy',        # DELETE:{{url}}/api/payments/<acc_id>/
        'patch': 'activate'         # PATCH: {{url}}/api/payments/<acc_id>/
    }), name='payment_account-detail'),

    # Пополнения для конкретного аккаунта
    path('payments/<int:account_id>/refills/', RefillViewSet.as_view({  # Не работает, переписать, выдаёт всё
        'get': 'list',              # GET : {{url}}/api/payments/
        'post': 'create'            # POST: {{url}}/api/payments/
    }), name='refill-list'),
    path('payments/<int:account_id>/refills/<int:pk>/', RefillViewSet.as_view({
        'get': 'retrieve',          # GET :
        'put': 'update',            # PUT :
        'delete': 'destroy'         # DELETE:
    }), name='refill-detail'),

    # Списания для конкретного аккаунта
    path('payments/<int:account_id>/deductions/', DeductionViewSet.as_view({
        'get': 'list',              # GET : {{url}}/payments/<acc_id>/deductions/
        'post': 'create'            # POST: {{url}}/payments/<acc_id>/deductions/
    }), name='deduction-list'),
    path('payments/<int:account_id>/deductions/<int:pk>/', DeductionViewSet.as_view({
        'get': 'retrieve',          # GET : {{url}}/payments/<acc_id>/deductions/<deduction_id>
        'delete': 'destroy'         #DELETE:{{url}}/payments/<acc_id>/deductions/<deduction_id>
    }), name='deduction-detail'),
    path('payments/<int:account_id>/deductions/<int:pk>/restore/', DeductionViewSet.as_view({
        'post': 'restore'           # POST: {{url}}/payments/<acc_id>/deductions/<deduction_id>/restore/
    }), name='deduction-restore'),

    # Просмотр всех пополненных счетов (только для админов)
    path('positive-balance-accounts/', PositiveBalanceAccountsView.as_view(), name='positive-balance-accounts'),

    # Обновление курса валют (только для админов)
    path("update-currency-rates/", UpdateCurrencyRatesAPIView.as_view(), name="update-currency-rates"),

    # Просмотр курса валют одного аккаунта по id относительно рубля
    path('payments/<int:account_id>/currency/', AccountCurrencyAPIView.as_view(), name='account_currency'),

    # Просмотр курсов валют всех аккаунтов пользователя относительно рубля
    path('currencies/', UserCurrenciesAPIView.as_view(), name='user-currencies'),

    # Просмотр курсов любой переданной валюты относительно рубля (POST)
    path('currency/rate/', CurrencyRateAPIView.as_view(), name='currency_rate'),

# Routes for Plan
    path('plans/', PlanViewSet.as_view({
        'get': 'list',              # GET :
        'post': 'create'            # POST:
    }), name='plan-list-create'),
    path('plans/<int:pk>/', PlanViewSet.as_view({
        'get': 'retrieve',          # GET :
        'put': 'update',            # PUT :
        'patch': 'partial_update',  # PATCH :
        'delete': 'destroy',        # DELETE :
    }), name='plan-detail'),

    # Routes for PromoCode
    path('promocodes/', PromoCodeViewSet.as_view({
        'get': 'list',              # GET :
        'post': 'create'            # POST:
    }), name='promocode-list-create'),
    path('promocodes/<int:pk>/', PromoCodeViewSet.as_view({
        'get': 'retrieve',          # GET :
        'put': 'update',            # PUT :
        'patch': 'partial_update',  # PATCH :
        'delete': 'destroy',        # DELETE :
    }), name='promocode-detail'),

    # Routes for UserPlan
    path('userplans/', UserPlanViewSet.as_view({
        'get': 'list',              # GET :
        'post': 'create'            # POST:
    }), name='userplan-list-create'),
    path('userplans/<int:pk>/', UserPlanViewSet.as_view({
        'get': 'retrieve',          # GET :
        'put': 'update',            # PUT :
        'patch': 'partial_update',  # PATCH :
        'delete': 'destroy',        # DELETE :
    }), name='userplan-detail'),

    # User accounts
    path('im/', UserViewSet.as_view({
        'get': 'me',                # GET : {{url}}/api/im/
    }), name='user-detail'),
    path('user/<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve',          # GET :  {{url}}/api/user/<user_id>/
        'patch': 'update',          # PATCH: {{url}}/api/user/<user_id>/
        'delete': 'destroy',        # DELETE:{{url}}/api/user/<user_id>/
    }), name='user-detail'),

    # User tokens
    path('tokens/', UserTokenViewSet.as_view({
        'get': 'list',              # GET : {{url}}/api/tokens/
        'post': 'create'            # POST: {{url}}/api/tokens/
    }), name='user-token-list'),
    path('tokens/<int:pk>/', UserTokenViewSet.as_view({
        'get': 'retrieve',          # GET :   {{url}}/api/tokens/<token_id>
        'delete': 'destroy'         # DELETE: {{url}}/api/tokens/<token_id>
    }), name='user-token-detail'),
]
