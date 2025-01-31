from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ..permissions import ZUserTokenPermission
from .tariff_serializers import PlanSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from .tariff_models import Plan
import datetime

now = datetime.datetime.now

class AdminPlanViewSet(viewsets.ModelViewSet):
    """
    CRUD для тарифов для администратора.
    Администратор видит все тарифы (включая архивированные и удалённые).
    """
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):
        """
        Мягкое удаление тарифа (is_active = False).
        """
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Архивация тарифа (is_archived = True).
        """
        plan = self.get_object()
        plan.is_archived = True
        plan.archived_in = now()
        plan.save()
        return Response({"detail": "Plan archived successfully."}, status=status.HTTP_200_OK)


class UserPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [ZUserTokenPermission]
    serializer = PlanSerializer()

    def get(self, request, *args, **kwargs):
        plans = Plan.objects.filter(is_active=True, is_archived = False)  # Показываем только активные тарифы
        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlanViewSet(viewsets.ModelViewSet):
    """
    Представление для CRUD тарифов.
    - Создание: только администратор
    - Чтение: только авторизованный пользователь
    - Изменение и удаление: только администратор
    """

    queryset = Plan.objects.filter(is_active=True)  # Показываем только активные тарифы
    serializer_class = PlanSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        """
        Мягкое удаление тарифа (is_active = False).
        """
        try:
            instance.is_active = False
            instance.save()
            return Response({"detail": "Plan remove successfully."}, status=status.HTTP_200_OK)
        except Plan.DoesNotExist:
            return Response({"detail": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def restore(self, request, pk=None):
        """
        Восстановление удалённого тарифа (is_active = True).
        Доступно только администратору.
        """
        try:
            plan = Plan.objects.get(pk=pk, is_active=False)  # Ищем удалённый тариф
            plan.is_active = True
            plan.save()
            return Response({"detail": "Plan restored successfully."}, status=status.HTTP_200_OK)
        except Plan.DoesNotExist:
            return Response({"detail": "Plan not found or already active."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """
        Архивация тарифа (is_archived = True).
        """
        plan = self.get_object()
        plan.is_archived = True
        plan.archived_in = now()
        plan.save()
        return Response({"detail": "Plan archived successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """
        Архивация тарифа (is_archived = True, archived_in = now).
        """
        plan = self.get_object()
        if plan.is_archived:
            return Response({"detail": "Plan is already archived."}, status=status.HTTP_400_BAD_REQUEST)

        plan.is_archived = True
        plan.archived_in = now()
        plan.save()

        return Response({"detail": "Plan archived successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def unarchive(self, request, pk=None):
        """
        Разархивация тарифа (is_archived = False).
        """
        plan = self.get_object()
        if not plan.is_archived:
            return Response({"detail": "Plan is not archived."}, status=status.HTTP_400_BAD_REQUEST)

        plan.is_archived = False
        plan.archived_in = None  # Сбрасываем дату архивации
        plan.save()

        return Response({"detail": "Plan unarchived successfully."}, status=status.HTTP_200_OK)
