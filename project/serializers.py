from rest_framework import serializers
from .models import Item

### Сериалайзер - класс, преобразующий
### данные из набора запроса (query set)
### в конечный json

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

# class ArticleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Article
#         fields = '__all__'