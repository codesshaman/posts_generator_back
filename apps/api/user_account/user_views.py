from .user_serializers import UserSerializer, UserRegistrationSerializer
from rest_framework import generics, permissions, status, viewsets, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from project.permissions import ZUserTokenPermission
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from project.language import translator
from project.models import User


# Регистрация нового пользователя
# Общедоступный метод
class UserRegistrationAPIView(views.APIView):
    permission_classes = [AllowAny]  # Разрешает доступ без аутентификации

    def post(self, request, *args, **kwargs):
        # Передаем context с request в сериализатор
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()  # Вызов метода create в сериализаторе

            if user.auth == 'email':
                message = translator(
                    "Пользователь успешно зарегистрирован. Пожалуйста, перейдите по ссылке активации, отправленной на указанный email.",
                    "User registered successfully. Please check your email for the activation link.",
                    self.request
                )
            elif user.auth == 'vk':
                message = translator(
                    "Пользователь успешно зарегистрирован через ВКонтакте. Вы можете войти в систему.",
                    "User successfully registered via VK. You can now log in.",
                    self.request
                )
            else:
                message = translator(
                    "Пользователь успешно зарегистрирован.",
                    "User registered successfully.",
                    self.request
                )

            return Response({"message": message}, status=status.HTTP_201_CREATED)

        # Возвращаем ошибки валидации
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GoogleAuthAPIView(views.APIView):
#     def post(self, request):
#         google_data = get_google_user_data(request.data['google_token'])  # Функция получения данных из Google
#         request.user_data = google_data  # Передача данных в сериализатор
#
#         serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Google аутентификация прошла успешно"}, status=201)
#         return Response(serializer.errors, status=400)


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
            raise PermissionDenied(translator(
                "Доступ запрещён. Вы можете работать только со своими данными.",
                "Access is denied. You can only work with your own data.",
                self.request
            ))

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
                {"detail": translator(
                    "Обратитесь к администратору за дополнительными правами.",
                    "Contact the administrator for additional rights.",
                    self.request
                )},
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
                {"detail": translator(
                    "Пользователь уже деактивирован.",
                    "The user has already been deactivated.",
                    self.request
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Устанавливаем is_active=False
        user.is_active = False
        user.save()

        return Response(
            {"detail": translator(
                "Пользователь был деактивирован.",
                "The user has been deactivated.",
                self.request
            )},
            status=status.HTTP_200_OK,
        )
