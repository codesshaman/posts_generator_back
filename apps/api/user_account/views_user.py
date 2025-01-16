from .serializer_user import UserSerializer, LoginSerializer, UserRegistrationSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from project.models import User


# Регистрация нового пользователя
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Доступно всем

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "User created successfully", "user": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


# Представление для просмотра/обновления текущего пользователя
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Только для аутентифицированных пользователей

    def get_object(self):
        return self.request.user  # Возвращаем текущего пользователя


# Представление для списка пользователей (административный доступ)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Доступ только для администратора

