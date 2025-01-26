from .promocode_models import PromoCode
from rest_framework import serializers


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'