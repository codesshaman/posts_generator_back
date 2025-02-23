"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from dotenv import load_dotenv
from django.contrib import admin
from django.urls import path, include

# Загружаем .env файл
load_dotenv()

# Получаем путь к админке
admin_path = os.getenv('ALLOWED_ADMIN', 'admin')

# Добавляем слеш, если его нет
if not admin_path.endswith('/'):
    admin_path += '/'

urlpatterns = [
    path(admin_path, admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('mail/', include('apps.mail.urls')),
]
