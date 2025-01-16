from .serializer_user import UserSerializer, UserRegistrationSerializer
from rest_framework import generics, permissions, status, viewsets, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from project.models import User


# Представление для списка пользователей (административный доступ)
class UserViewSet(viewsets.ReadOnlyModelViewSet):  # Только для чтения
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Доступ только для администратора


# Регистрация нового пользователя
# Общедоступный метод
class UserRegistrationAPIView(views.APIView):
    permission_classes = [AllowAny]  # Разрешает доступ без аутентификации
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        # Возвращаем ошибки валидации
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Представление для просмотра/обновления текущего пользователя
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Только для аутентифицированных пользователей

    def get_object(self):
        return self.request.user  # Возвращаем текущего пользователя

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        # Проверка, чтобы пользователь мог получить только свои данные
        if request.user.id != user_id:
            return Response(
                {"detail": "Доступ запрещён. Вы можете получить только свои данные."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id, *args, **kwargs):
        # Проверка, чтобы пользователь мог изменять только свои данные
        if request.user.id != user_id:
            return Response(
                {"detail": "Доступ запрещён. Вы можете изменять только свои данные."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = get_object_or_404(User, id=user_id)

        # Сериализатор для частичного обновления данных пользователя
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id, *args, **kwargs):
        # Проверка, чтобы пользователь мог изменять только свои данные
        if request.user.id != user_id:
            return Response(
                {"detail": "Доступ запрещён. Вы можете изменять только свои данные."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = get_object_or_404(User, id=user_id)

        # Сериализатор для полного обновления данных пользователя
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
