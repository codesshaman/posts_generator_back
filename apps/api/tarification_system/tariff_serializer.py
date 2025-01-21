from rest_framework import serializers
from .tariff_model import Plan, PromoCode, UserPlan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'


class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlan
        fields = '__all__'
