from .vk_groups.vk_groups_views import VkGroupViewSet, VkGroupsViewSet
from .vk_groups.vk_group_token_views import VkGroupTokenViewSet
from django.urls import path


urlpatterns = [
    path('vkgroups/', VkGroupViewSet.as_view({
        'get': 'list',              # GET : {{url}}/vk/vkgroups/
        'post': 'create'            # POST: {{url}}/vk/vkgroups/
    }), name='vkgroup-list-create'),
    path('vkgroups/<group_id>/', VkGroupsViewSet.as_view({
        'get': 'retrieve',          # GET :  {{url}}/vk/vkgroups/<group_id>/
        'put': 'update',            # PUT :  {{url}}/vk/vkgroups/<group_id>/
        'patch': 'partial_update',  # PATCH :{{url}}/vk/vkgroups/<group_id>/
        'delete': 'destroy'         # DELETE:{{url}}/vk/vkgroups/<group_id>/
    }), name='vkgroup-detail'),
    path('vkgrouptokens/', VkGroupTokenViewSet.as_view({
        'get': 'list',              # GET : {{url}}/vk/vkgrouptokens/
        'post': 'create'            # POST: {{url}}/vk/vkgrouptokens/
    }), name='vkgroup-token-list-create'),
    path('vkgrouptokens/<token_id>/', VkGroupsViewSet.as_view({
        'get': 'retrieve',          # GET :  {{url}}/vk/vkgrouptokens/<token_id>/
        'put': 'update',            # PUT :  {{url}}/vk/vkgrouptokens/<token_id>/
        'patch': 'partial_update',  # PATCH :{{url}}/vk/vkgrouptokens/<token_id>/
        'delete': 'destroy'         # DELETE:{{url}}/vk/vkgrouptokens/<token_id>/
    }), name='vkgroup-token-detail'),
]