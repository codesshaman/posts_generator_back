from rest_framework.exceptions import PermissionDenied
from .tokens_serializers import UserTokenSerializer
from django.utils.timezone import now, timedelta
from django.shortcuts import get_object_or_404
from project.permissions import ZUserTokenPermission
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from project.language import translator
from django.db import IntegrityError
from .tokens_models import UserToken


class UserTokenViewSet(ViewSet):
    """
    ViewSet для управления токенами:
    - Пользователи могут управлять только своими токенами.
    - Администраторы могут управлять любыми токенами.
    """
    permission_classes = [ZUserTokenPermission]


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
            return Response({"error": translator(
                "Поле 'name' обязательно для создания токена.",
                "The 'name' field is required to create a token.",
                self.request
            )}, status=400)

        expires_in_days = request.data.get('expires_in_days', 30)  # По умолчанию 30 дней
        try:
            expires_in_days = int(expires_in_days)
        except ValueError:
            return Response({"error": translator(
                "Поле 'expires_in_days' должно быть числом.",
                "The 'expires_in_days' field must be a number.",
                self.request
            )}, status=400)

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
            return Response({"error": translator(
                "Токен с таким именем уже существует.",
                "A token with that name already exists.",
                self.request
            )}, status=400)

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
            raise PermissionDenied(translator(
                "Вы не можете удалить токен, который вам не принадлежит.",
                "You cannot delete a token that does not belong to you.",
                self.request
            ))
        token.delete()
        return Response({"detail": translator(
            "Токен успешно удален.",
            "The token has been successfully deleted.",
            self.request
        )}, status=204)
