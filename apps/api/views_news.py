from rest_framework import viewsets
from .models import New
from .serializer_news import NewsSerializer

class NewsViewSet(viewsets.ModelViewSet):
    queryset = New.objects.all().order_by('-created_at')  # Сортировка по дате создания
    serializer_class = NewsSerializer