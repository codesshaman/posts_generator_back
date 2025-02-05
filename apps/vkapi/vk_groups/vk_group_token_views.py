from .vk_group_models import VkGroupToken
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .vk_group_serializers import VkGroupTokenSerializer

class IsGroupOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только владельцам группы или администраторам.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.group.user == request.user

class VkGroupTokenViewSet(viewsets.ModelViewSet):
    serializer_class = VkGroupTokenSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupOwnerOrAdmin]

    def get_queryset(self):
        """
        Администратор видит все токены, пользователь — только токены своих групп.
        """
        if self.request.user.is_staff:
            return VkGroupToken.objects.all()
        return VkGroupToken.objects.filter(group__user=self.request.user)

    def perform_create(self, serializer):
        """
        Проверяет, что пользователь создаёт токен только для своей группы.
        """
        group = serializer.validated_data['group']
        if not self.request.user.is_staff and group.user != self.request.user:
            raise PermissionDenied("Вы можете управлять только своими группами.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Удаление токена доступно только владельцу группы или администратору.
        """
        token = self.get_object()
        if not request.user.is_staff and token.group.user != request.user:
            raise PermissionDenied("Вы можете удалять только свои токены.")
        return super().destroy(request, *args, **kwargs)
