from rest_framework import serializers
from .models import New

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = New
        fields = '__all__'  # Все поля модели