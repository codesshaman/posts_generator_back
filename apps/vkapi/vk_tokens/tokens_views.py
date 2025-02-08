from rest_framework.exceptions import PermissionDenied
from .tokens_serializers import VKTokenSerializer
from django.utils.timezone import now, timedelta
from django.shortcuts import get_object_or_404
from project.permissions import ZUserTokenPermission
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from project.language import translator
from django.db import IntegrityError
from .tokens_models import VKToken


class VKTokensViewSet(ViewSet):
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
            return VKToken.objects.all()  # Администраторы видят все токены
        return VKToken.objects.filter(user=user)  # Обычные пользователи видят только свои токены


    def list(self, request):
        """
        Список токенов текущего пользователя.
        """
        queryset = self.get_queryset()
        serializer = VKTokenSerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        """
        Создание нового токена с пользовательским именем.
        """
        print('test')
        user = request.user
        name = request.data.get('name', '').strip()
        if not name:
            return Response({"error": translator(
                "Поле 'name' обязательно для создания токена.",
                "The 'name' field is required to create a token.",
                self.request
            )}, status=400)
        token = request.data.get('token', '').strip()
        if not token:
            return Response({"error": translator(
                "Введите ваш токен.",
                "Write your token.",
                self.request
            )}, status=400)

        # Создание токена
        try:
            token = VKToken.objects.create(
                user=user,
                name=name,
                token=token,
            )
        except IntegrityError:
            return Response({"error": translator(
                "Токен уже существует.",
                "The token already exists.",
                self.request
            )}, status=400)

        serializer = VKTokenSerializer(token)
        return Response(serializer.data, status=201)


    def retrieve(self, request, pk=None):
        """
        Получить информацию о токене.
        """
        queryset = self.get_queryset()
        token = get_object_or_404(queryset, pk=pk)
        serializer = VKTokenSerializer(token)
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
