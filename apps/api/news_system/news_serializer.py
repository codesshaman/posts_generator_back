from rest_framework import serializers
from .news_model import New


class NewSerializer(serializers.ModelSerializer):
    class Meta:
        model = New
        fields = ['id',
                  'title',
                  'description',
                  'image_url',
                  'content',
                  'created_at',
                  'updated_at'
                  ]
