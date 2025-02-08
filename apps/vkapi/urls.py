from .vk_groups.vk_groups_views import VkGroupsViewSet
from .vk_tokens.tokens_views import VKTokensViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path


# Роутер для автоматического создания маршрутов
router = DefaultRouter()

urlpatterns = [
    # Работа с группами ВК
    path('vkgroups/', VkGroupsViewSet.as_view({
        'get': 'list',              # GET : {{url}}/vk/vkgroups/
        'post': 'create'            # POST: {{url}}/vk/vkgroups/
    }), name='vkgroup-list-create'),
    path('vkgroups/<group_id>/', VkGroupsViewSet.as_view({
        'get': 'retrieve',          # GET :  {{url}}/vk/vkgroups/<group_id>/
        'put': 'update',            # PUT :  {{url}}/vk/vkgroups/<group_id>/
        'patch': 'partial_update',  # PATCH :{{url}}/vk/vkgroups/<group_id>/
        'delete': 'destroy'         # DELETE:{{url}}/vk/vkgroups/<group_id>/
    }), name='vkgroup-detail'),
    # Работа с токенами Вк
    path('vktokens/', VKTokensViewSet.as_view({
        'get': 'list',              # GET : {{url}}/api/vktokens/
        'post': 'create'            # POST: {{url}}/api/vktokens/
    }), name='vk-tokens-list'),
    path('vktokens/<int:pk>/', VKTokensViewSet.as_view({
        'get': 'retrieve',          # GET :   {{url}}/api/vktokens/<token_id>/
        'delete': 'destroy'         # DELETE: {{url}}/api/vktokens/<token_id>/
    }), name='vk-token-detail'),
]