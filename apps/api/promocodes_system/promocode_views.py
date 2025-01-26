from .promocode_serializers import PromoCodeSerializer
from rest_framework.permissions import AllowAny
from .promocode_models import PromoCode
from django.utils.timezone import now
from rest_framework import viewsets



# Представление для PromoCode
class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        """При удалении переводим промокод в архив вместо реального удаления."""
        instance.is_archived = True
        instance.archived_in = now()
        instance.save()