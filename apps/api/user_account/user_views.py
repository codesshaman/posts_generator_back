from .user_serializers import UserSerializer, UserRegistrationSerializer
from rest_framework import generics, permissions, status, viewsets, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from ..permissions import ZUserTokenPermission
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from project.models import User


# Регистрация нового пользователя
# Общедоступный метод
class UserRegistrationAPIView(views.APIView):
    permission_classes = [AllowAny]  # Разрешает доступ без аутентификации

    def post(self, request, *args, **kwargs):
        # Передаем context с request в сериализатор
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # Вызов метода create в сериализаторе
            return Response(
                {"message": "User registered successfully. Please check your email for the activation link."},
                status=status.HTTP_201_CREATED,
            )
        # Возвращаем ошибки валидации
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ViewSet):
    permission_classes = [ZUserTokenPermission]

    def get_object(self, pk=None):
        """
        Возвращает объект пользователя в зависимости от прав текущего пользователя.
        """
        user = self.request.user

        # Если администратор, разрешить доступ к любому пользователю
        if user.is_staff:
            return get_object_or_404(User, id=pk)

        # Если обычный пользователь, ограничить доступ только к своим данным
        if pk is None or user.id != int(pk):
            raise PermissionDenied("Доступ запрещён. Вы можете работать только со своими данными.")

        return get_object_or_404(User, id=pk)

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        """
        Возвращает данные текущего авторизованного пользователя.
        """
        user = request.user  # Получаем текущего пользователя из request
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)

    def retrieve(self, request, pk=None):
        """
        Получение данных пользователя по ID.
        """
        user = self.get_object(pk)  # Используем проверку через get_object
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Частичное обновление данных пользователя.
        """
        user = self.get_object(pk)  # Используем проверку через get_object

        # Проверка на попытку изменить is_staff
        if 'is_staff' in request.data and not request.user.is_staff:
            return Response(
                {"detail": "Обратитесь к администратору за дополнительными правами."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Сериализатор для обновления данных пользователя
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Мягкое удаление пользователя (установка is_active=False).
        """
        user = self.get_object(pk)  # Проверяем права через get_object

        # Если пользователь уже не активен
        if not user.is_active:
            return Response(
                {"detail": "Пользователь уже деактивирован."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Устанавливаем is_active=False
        user.is_active = False
        user.save()

        return Response(
            {"detail": f"Пользователь с ID {user.id} был деактивирован."},
            status=status.HTTP_200_OK,
        )
