from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .news_serializer import NewSerializer
from .news_model import New


class NewViewSet(ModelViewSet):
    """
    ViewSet для управления новостями.
    - Администраторы могут выполнять все CRUD-операции.
    - Обычные пользователи могут только просматривать активные новости.
    """
    serializer_class = NewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    def get_queryset(self):
        """
        Возвращает набор новостей.
        - Администраторы видят все записи.
        - Обычные пользователи видят только активные новости.
        """
        user = self.request.user
        if user.is_staff:
            return New.objects.all()  # Администраторы видят все новости
        return New.objects.filter(is_active=True)  # Обычные пользователи видят только активные новости


    def create(self, request, *args, **kwargs):
        """
        Создание новости.
        Доступно только администраторам.
        """
        user = request.user
        if not user.is_staff:
            return Response(
                {"detail": "Вы не имеете права создавать новости."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        """
        Полное обновление новости.
        Доступно только администраторам.
        """
        user = request.user
        if not user.is_staff:
            return Response(
                {"detail": "Вы не имеете права редактировать новости."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


    def partial_update(self, request, *args, **kwargs):
        """
        Редактирование полей новости.
        Доступно только администраторам.
        """
        user = request.user
        if not user.is_staff:
            return Response(
                {"detail": "Вы не имеете права редактировать поля новости."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)


    def destroy(self, request, *args, **kwargs):
        """
        Удаление новости.
        Доступно только администраторам.
        """
        user = request.user
        if not user.is_staff:
            return Response(
                {"detail": "Вы не имеете права удалять новости."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
