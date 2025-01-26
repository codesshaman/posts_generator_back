from rest_framework import serializers
from .news_models import New


class NewSerializer(serializers.ModelSerializer):
    class Meta:
        model = New
        fields = [
            'id',
            'title',
            'description',
            'image_url',
            'content',
            'is_active',
            'created_at',
            'updated_at',
        ]