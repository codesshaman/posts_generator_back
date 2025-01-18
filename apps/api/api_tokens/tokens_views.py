from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from .tokens_serializer import UserTokenSerializer
from django.db import IntegrityError
from .tokens_model import UserToken


class UserTokenListCreateAPIView(ListCreateAPIView):
    """
    Список токенов текущего пользователя и создание нового токена.
    """
    serializer_class = UserTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError("Токен с таким именем уже существует.")


class UserTokenRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    """
    Удаление токена или получение его деталей.
    """
    serializer_class = UserTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserToken.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Вы не можете удалить токен, который вам не принадлежит.")
        super().perform_destroy(instance)
