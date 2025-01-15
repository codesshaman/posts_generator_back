from .news_system.views_new import NewListCreateView, NewDetailView, NewViewSet
from .user_account.views_user import RegisterView, LoginView, UserDetailView
# from .views_user import UserListView, UserDetailView
from rest_framework.routers import DefaultRouter
from django.urls import path, include
# from .views_user import UserViewSet
from django.urls import path

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
    # path('user/', UserListView.as_view(), name='user-list'),  # JSON списка пользователей
    # path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),  # JSON конкретного пользователя

    # Маршруты для создания пользователей / входа
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserDetailView.as_view(), name='user-detail'),

]
