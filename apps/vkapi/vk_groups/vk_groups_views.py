from .vk_group_serializers import VkGroupSerializer, VkGroupTokenSerializer
from rest_framework import viewsets, permissions, status
from project.permissions import ZUserTokenPermission
from .vk_group_models import VkGroup, VkGroupToken
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action



class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ пользователям только к своим группам, а администраторам — ко всем.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user

class VkGroupViewSet(viewsets.ModelViewSet):
    """
    Представление для CRUD-операций над VkGroup для обычных пользователей.
    """
    serializer_class = VkGroupSerializer
    permission_classes = [ZUserTokenPermission]

    def get_queryset(self):
        return VkGroup.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VkGroupsViewSet(viewsets.ViewSet):
    """
    Представление для CRUD-операций VkGroup.
    """
    permission_classes = [ZUserTokenPermission, IsOwnerOrAdmin]

    def get_object(self, group_id):
        """
        Получает объект VkGroup с проверкой прав доступа.
        """
        if self.request.user.is_staff:
            return get_object_or_404(VkGroup, group_id=group_id)
        return get_object_or_404(VkGroup, group_id=group_id, user=self.request.user)

    def retrieve(self, request, group_id=None):
        group = self.get_object(group_id)
        serializer = VkGroupSerializer(group)
        return Response(serializer.data)

    def list(self, request):
        queryset = VkGroup.objects.all() if request.user.is_staff else VkGroup.objects.filter(user=request.user)
        serializer = VkGroupSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = VkGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, group_id=None):
        group = self.get_object(group_id)
        serializer = VkGroupSerializer(group, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()  # автоматически обновит `updated_at`
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, group_id=None):
        group = self.get_object(group_id)
        serializer = VkGroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # автоматически обновит `updated_at`
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, group_id=None):
        group = self.get_object(group_id)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VkGroupTokenViewSet(viewsets.ModelViewSet):
    """
    Представление для CRUD-операций над VkGroupToken.
    """
    queryset = VkGroupToken.objects.all()
    serializer_class = VkGroupTokenSerializer
