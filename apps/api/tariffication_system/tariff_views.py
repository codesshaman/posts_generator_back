from rest_framework.permissions import IsAuthenticated, IsAdminUser
from project.permissions import ZUserTokenPermission
from .tariff_serializers import PlanSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status
from project.language import translator
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
        return Response({"detail": translator(
            "Тариф успешно архивирован.",
            "Plan archived successfully.",
            self.request
        )}, status=status.HTTP_200_OK)


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
            return Response({"detail": translator(
                "Тариф успешно удалён",
                "Plan remove successfully.",
                self.request
            )}, status=status.HTTP_200_OK)
        except Plan.DoesNotExist:
            return Response({"detail": translator("Plan not found.")}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({"detail": translator(
                "Тариф успещно восстановлен.",
                "Plan restored successfully.",
                self.request
            )}, status=status.HTTP_200_OK)
        except Plan.DoesNotExist:
            return Response({"detail": translator(
                "Тариф не найден или уже активен.",
                "Plan not found or already active.",
                self.request
            )}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """
        Архивация тарифа (is_archived = True).
        """
        plan = self.get_object()
        plan.is_archived = True
        plan.archived_in = now()
        plan.save()
        return Response({"detail": translator(
            "Тариф успешно архивирован.",
            "Plan archived successfully.",
            self.request
        )}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """
        Архивация тарифа (is_archived = True, archived_in = now).
        """
        plan = self.get_object()
        if plan.is_archived:
            return Response({"detail": translator(
                "Тариф уже был архивирован.",
                "Plan is already archived.",
                self.request
            )}, status=status.HTTP_400_BAD_REQUEST)

        plan.is_archived = True
        plan.archived_in = now()
        plan.save()

        return Response({"detail": translator(
            "Тариф успешно архивирован.",
            "Plan archived successfully.",
            self.request
        )}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def unarchive(self, request, pk=None):
        """
        Разархивация тарифа (is_archived = False).
        """
        plan = self.get_object()
        if not plan.is_archived:
            return Response({"detail": translator(
                "Данный тариф не был архивирован.",
                "Plan is not archived.",
                self.request
            )}, status=status.HTTP_400_BAD_REQUEST)

        plan.is_archived = False
        plan.archived_in = None  # Сбрасываем дату архивации
        plan.save()

        return Response({"detail": translator(
            "Тариф успешно разархивирован.",
            "Plan unarchived successfully.",
            self.request
        )}, status=status.HTTP_200_OK)
