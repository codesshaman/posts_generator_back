from .user_account.views_user import UserDetailAPIView, UserViewSet, UserRegistrationAPIView, UserDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .news_system.views_new import NewListCreateView, NewDetailView, NewViewSet
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
