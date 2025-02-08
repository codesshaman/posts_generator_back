from .vk_group_models import VkGroup
from rest_framework import serializers


class VkGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = VkGroup
        fields = ['group_id', 'user', 'vk_id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['group_id', 'user', 'created_at', 'updated_at']  # Убираем эти поля из редактируемых

    def update(self, instance, validated_data):
        # Убираем vk_id и group_id из данных, чтобы они не могли быть обновлены
        validated_data.pop('vk_id', None)
        validated_data.pop('group_id', None)

        # Обновляем instance с новыми данными
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Сохраняем обновленный объект и возвращаем его
        instance.save()
        return instance
