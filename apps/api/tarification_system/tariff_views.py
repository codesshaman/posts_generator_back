from .tariff_serializers import PlanSerializer, UserPlanSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status
from .tariff_models import Plan, UserPlan
import datetime

now = datetime.datetime.now

# Представление для Plan
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        """При удалении переводим тариф в архив вместо реального удаления."""
        instance.is_archived = True
        instance.archived_in = now()
        instance.save()


# Представление для UserPlan
class UserPlanViewSet(viewsets.ModelViewSet):
    queryset = UserPlan.objects.select_related('user', 'plan', 'promo').all()
    serializer_class = UserPlanSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Добавляем проверку на уникальность тарифа для пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Проверка на существующий активный тариф
        user = request.user
        existing_plan = UserPlan.objects.filter(user=user, expire_at__gte=now()).exists()
        if existing_plan:
            return Response(
                {"detail": "User already has an active plan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
