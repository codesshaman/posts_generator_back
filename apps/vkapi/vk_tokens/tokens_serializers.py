from rest_framework import serializers
from .tokens_models import VKToken

class VKTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = VKToken
        fields = ['id', 'name', 'token', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
