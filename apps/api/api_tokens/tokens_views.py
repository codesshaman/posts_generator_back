from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .tokens_serializer import UserTokenSerializer
from django.utils.timezone import now, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.db import IntegrityError
from .tokens_model import UserToken


class UserTokenViewSet(ViewSet):
    """
    ViewSet для управления токенами:
    - Пользователи могут управлять только своими токенами.
    - Администраторы могут управлять любыми токенами.
    """
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        """
        Возвращает токены в зависимости от прав пользователя.
        """
        user = self.request.user
        if user.is_staff:
            return UserToken.objects.all()  # Администраторы видят все токены
        return UserToken.objects.filter(user=user)  # Обычные пользователи видят только свои токены


    def list(self, request):
        """
        Список токенов текущего пользователя.
        """
        queryset = self.get_queryset()
        serializer = UserTokenSerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        """
        Создание нового токена с пользовательским именем.
        """
        user = request.user
        name = request.data.get('name', '').strip()  # Получаем имя токена из запроса
        if not name:
            return Response({"error": "Поле 'name' обязательно для создания токена."}, status=400)

        expires_in_days = request.data.get('expires_in_days', 30)  # По умолчанию 30 дней
        try:
            expires_in_days = int(expires_in_days)
        except ValueError:
            return Response({"error": "Поле 'expires_in_days' должно быть числом."}, status=400)

        expires_at = now() + timedelta(days=expires_in_days)

        # Генерация уникального токена (пример: UUID)
        from uuid import uuid4
        token_value = str(uuid4())

        # Создание токена
        try:
            token = UserToken.objects.create(
                user=user,
                name=name,  # Устанавливаем имя токена
                token=token_value,
                expires_at=expires_at
            )
        except IntegrityError:
            return Response({"error": "Токен с таким именем уже существует."}, status=400)

        serializer = UserTokenSerializer(token)
        return Response(serializer.data, status=201)


    def retrieve(self, request, pk=None):
        """
        Получить информацию о токене.
        """
        queryset = self.get_queryset()
        token = get_object_or_404(queryset, pk=pk)
        serializer = UserTokenSerializer(token)
        return Response(serializer.data)


    def destroy(self, request, pk=None):
        """
        Удалить токен.
        """
        queryset = self.get_queryset()
        token = get_object_or_404(queryset, pk=pk)
        if not request.user.is_staff and token.user != request.user:
            raise PermissionDenied("Вы не можете удалить токен, который вам не принадлежит.")
        token.delete()
        return Response({"detail": "Токен успешно удален."}, status=204)
