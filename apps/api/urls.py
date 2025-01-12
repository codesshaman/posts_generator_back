from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_news import NewsViewSet

# Роутер для автоматического создания маршрутов
router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')  # URL: /api/news/

urlpatterns = [
    path('', include(router.urls)),  # Подключение всех маршрутов из роутера
]
