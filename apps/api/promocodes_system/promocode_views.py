from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .promocode_models import PromoCode
from .promocode_serializers import PromoCodeSerializer
import datetime


class PromoCodeViewSet(viewsets.ModelViewSet):
    """
    Представление для управления промокодами.
    CRUD-операции доступны только администраторам.
    """
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    lookup_field = 'promo_id'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'restore', 'archive', 'unarchive']:
            return [IsAdminUser()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        """
        Мягкое удаление промокода (is_active = False).
        """
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['patch'], url_path='restore', url_name='restore')
    def restore(self, request, promo_id=None):
        """
        Восстановление промокода (is_active = True).
        """
        promocode = self.get_object()  # Получаем объект PromoCode
        if promocode.is_active:
            return Response({"detail": "Промокод уже активен."}, status=status.HTTP_400_BAD_REQUEST)

        promocode.is_active = True
        promocode.save()
        return Response({"detail": "Промокод успешно восстановлен."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='archive', url_name='archive')
    def archive(self, request, promo_id=None):
        """
        Метод для архивации промокода.
        """
        promocode = self.get_object()  # Получаем объект по promo_id
        if promocode.is_archived:
            return Response({"detail": "Промокод уже архивирован."}, status=status.HTTP_400_BAD_REQUEST)

        promocode.is_archived = True
        promocode.archived_in = datetime.datetime.now()  # Устанавливаем текущую дату/время
        promocode.save()
        return Response({"detail": "Промокод успешно архивирован."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='archive', url_name='archive')
    def unarchive(self, request, promo_id=None):
        """
        Метод для архивации промокода.
        """
        promocode = self.get_object()  # Получаем объект по promo_id
        if promocode.is_archived:
            promocode.is_archived = False
            promocode.save()
            return Response({"detail": "Промокод успешно разархивирован."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Промокод не архивирован."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def get_by_code(self, request):
        """
        Получение промокода по уникальному полю `code`.
        Доступно всем пользователям.
        """
        code = request.data.get("code")
        if not code:
            return Response({"detail": "Promo code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            promo = PromoCode.objects.get(code=code, is_active=True, is_archived=False)
            serializer = self.get_serializer(promo)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PromoCode.DoesNotExist:
            return Response({"detail": "Promo code not found or archived."}, status=status.HTTP_404_NOT_FOUND)
