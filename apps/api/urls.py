from .user_account.user_views import UserDetailAPIView, UserViewSet, UserRegistrationAPIView, UserDetailView
from .payment_account.payment_views import PaymentAccountViewSet, RefillViewSet, DeductionViewSet
from .api_tokens.tokens_views import UserTokenListCreateAPIView, UserTokenRetrieveDestroyAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .news_system.news_views import NewListCreateView, NewDetailView, NewViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include


# Роутер для автоматического создания маршрутов
router = DefaultRouter()
router.register(r'news', NewViewSet, basename='news')  # URL: /api/news/
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),  # Подключение всех маршрутов из роутера

    # Маршруты для новостей
    path('news/', NewListCreateView.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewDetailView.as_view(), name='news-detail'),

    # Маршруты для пользователей
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('user/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('me/', UserDetailView.as_view(), name='user-detail'),

    # # Маршруты для получения / обновления JWT-токенов
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # # Маршруты для получения / обновления пользовательских токенов
    path('tokens/', UserTokenListCreateAPIView.as_view(), name='user-token-list'),
    path('tokens/<int:pk>/', UserTokenRetrieveDestroyAPIView.as_view(), name='user-token-detail'),

    # Платёжные аккаунты
    path('payments/', PaymentAccountViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment_account-list'),
    path('payments/<int:pk>/', PaymentAccountViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='payment_account-detail'),

    # Пополнения для конкретного аккаунта
    path('payments/<int:account_id>/refills/', RefillViewSet.as_view({'get': 'list', 'post': 'create'}), name='refill-list'),
    path('payments/<int:account_id>/refills/<int:pk>/', RefillViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='refill-detail'),

    # Списания для конкретного аккаунта
    path('payments/<int:account_id>/deductions/', DeductionViewSet.as_view({'get': 'list', 'post': 'create'}), name='deduction-list'),
    path('payments/<int:account_id>/deductions/<int:pk>/', DeductionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='deduction-detail'),

]


################## API LIST ##################
### New user registration (open api for all):
### POST: http://127.0.0.1:8000/api/register/
### Content-Type: application/json
### json: {
### "login": "new_user_login",
### "email": "new_user_email@example.com",
### "name": "baby",
### "surname": "baby",
### "password": "secur333epassword444",
### "password_confirm": "secur333epassword444",
### "referrer": "1"
### }
#############################################
### Get token for user session
### POST: http://127.0.0.1:8000/api/token/
### json: {
### "login": "user_login",
### "password": "user_password"
### }
#############################################
### Refresh token for user session
### POST: http://127.0.0.1:8000/api/token/refresh/
### json: {
### "refresh": "refresh_token"
### }
#############################################
### Viewing and changind user data
### PATCH: http://127.0.0.1:8000/api/user/<user_id>/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
### json: {
### "changet_field": "changed_value",
### "changet_field2": "changed_value2"
### }
#############################################
### Get user data for authorizen user
### GET: http://127.0.0.1:8000/api/users/<user_id>/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
#############################################
### Get user tokens list for authorizen user
### GET: http://127.0.0.1:8000/api/tokens/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
#############################################
### View user tokens list for authorizen user
### GET: http://127.0.0.1:8000/api/tokens/<token_id>/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
#############################################
### Create new token for authorizen user
### POST: http://127.0.0.1:8000/api/tokens/<user_id>/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
### json: {
### "name": "My New Token",
### "expires_in_days": 90
### }
#############################################
### Remove user tokens by id for authorizen user
### DELETE: http://127.0.0.1:8000/api/tokens/<token_id>/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
#############################################
### Create payment account with first payment
### POST: http://127.0.0.1:8000/api/payments/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>
### json: {
### "balance": <sum>,
### "currency": "RUB",
### "status": "active" ("frozen" if "balance": 0)
### }
#############################################
### View payment account for authorizen user
### GET: http://127.0.0.1:8000/api/payments/
### Content-Type: application/json
### Authorization: Bearer <refresh_token>