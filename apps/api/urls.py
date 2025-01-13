from .views_news import NewListCreateView, NewDetailView
from .views_user import UserListView, UserDetailView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views_news import NewViewSet
from .views_user import UserViewSet
from django.urls import path

# Роутер для автоматического создания маршрутов
router = DefaultRouter()
router.register(r'news', NewViewSet, basename='news')  # URL: /api/news/
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),  # Подключение всех маршрутов из роутера

    # Маршруты для новостей
    path('news/', NewListCreateView.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewDetailView.as_view(), name='news-detail'),

    # Маршруты для пользователей
    path('user/', UserListView.as_view(), name='user-list'),  # JSON списка пользователей
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),  # JSON конкретного пользователя
]
