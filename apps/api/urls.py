from .news_system.views_new import NewListCreateView, NewDetailView, NewViewSet
# from .views_user import UserListView, UserDetailView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.urls import path

from .user_account.views_user import UserRegistrationView, UserDetailView, UserListView

# Роутер для автоматического создания маршрутов
router = DefaultRouter()
router.register(r'news', NewViewSet, basename='news')  # URL: /api/news/
# router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),  # Подключение всех маршрутов из роутера

    # Маршруты для новостей
    path('news/', NewListCreateView.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewDetailView.as_view(), name='news-detail'),

    # Маршруты для пользователей
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='user-list'),

    # Маршруты для создания пользователей / входа
    path('register/', UserRegistrationView.as_view(), name='user-register'),


]
