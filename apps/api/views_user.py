from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializer_user import UserSerializer
from .model_user import User
import json


# Utility function to parse JSON request data
def parse_json_request(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


### Метод для просмотра списка пользователей
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Представление для просмотра и создания пользователя
@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    def get(self, request):
        users = User.objects.all().values()
        return JsonResponse(list(users), safe=False, status=200)

    def post(self, request):
        data = parse_json_request(request)
        if not data:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        try:
            # Create user with auto-generated values for registered_at and updated_at
            user = User.objects.create(
                referrer=data.get('referrer', 0),
                login=data['login'],
                password=data['password'],
                email=data['email'],
                name=data.get('name', ''),
                surname=data.get('surname', ''),
                avatar=data.get('avatar', ''),
                tariff=data.get('tariff', 0),
                balance=data.get('balance', 0),
            )

            # Handle achievements, refills, and deductions if provided in the request
            achievements = data.get('achievements', [])
            if achievements:
                user.achievements = achievements

            user.save()
            return JsonResponse({'id': user.id}, status=201)
        except (KeyError, ValidationError) as e:
            return JsonResponse({'error': str(e)}, status=400)


# Представление для обновления / удаления пользователя
@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return JsonResponse({
            'id': user.id,
            'referrer': user.referrer,
            'registered_at': user.registered_at,
            'updated_at': user.updated_at,
            'login': user.login,
            'email': user.email,
            'name': user.name,
            'surname': user.surname,
            'avatar': user.avatar,
            'tariff': user.tariff,
            'balance': user.balance,
            'api_token': user.api_token,
            'achievements': user.achievements,
            # Add other fields like refills and deductions if necessary
        }, status=200)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        data = parse_json_request(request)
        if not data:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        try:
            # Update user with provided data, or keep existing values
            user.login = data.get('login', user.login)
            user.password = data.get('password', user.password)
            user.email = data.get('email', user.email)
            user.name = data.get('name', user.name)
            user.surname = data.get('surname', user.surname)
            user.avatar = data.get('avatar', user.avatar)
            user.tariff = data.get('tariff', user.tariff)
            user.balance = data.get('balance', user.balance)

            # Optionally update achievements
            if 'achievements' in data:
                user.achievements = data['achievements']

            user.save()
            return JsonResponse({'message': 'User updated successfully'}, status=200)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=204)
