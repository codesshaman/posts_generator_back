from .user_account.views_user import UserDetailAPIView, UserViewSet, UserRegistrationAPIView, UserDetailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .news_system.views_new import NewListCreateView, NewDetailView, NewViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.urls import path


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
    # path('users/', UserListView.as_view(), name='user-list'),
    #
    # # Маршруты для создания пользователей / входа
    # path('register/', UserRegistrationView.as_view(), name='user-register'),
    # # Маршруты для получения / обновления JWT-токенов
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
