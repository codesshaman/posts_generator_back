from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .model_user import User


class UserSerializer(serializers.ModelSerializer):
    """
        Сериализатор для просмотра всех пользователей
    """
    class Meta:
        model = User
        fields = '__all__'  # или укажите нужные поля

    password = serializers.CharField(write_only=True)

class UserDetailView(APIView):
    """
    Сериализатор для получения информации о пользователе по его id.
    """
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RefillSerializer(serializers.ModelSerializer):
    class Meta:
        model = User.Refill
        fields = ['id', 'refill_datetime', 'refill_amount']


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User.Deduction
        fields = [
            'id', 'deduction_datetime', 'deduction_amount',
            'model', 'content', 'content_size'
        ]


class ReferralPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User.Referral.ReferralPayment
        fields = ['id', 'payment_datetime', 'payment_amount']


class ReferralSerializer(serializers.ModelSerializer):
    referral_payments = ReferralPaymentSerializer(many=True)

    class Meta:
        model = User.Referral
        fields = ['id', 'referral_id', 'referral_level', 'referral_payments']


class UserSerializer(serializers.ModelSerializer):
    refills = RefillSerializer(many=True, required=False)
    deductions = DeductionSerializer(many=True, required=False)
    referrals = ReferralSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'referrer', 'registered_at', 'updated_at',
            'login', 'email', 'name', 'surname', 'avatar',
            'tariff', 'balance', 'achievements', 'refills', 'deductions',
            'referrals', 'api_token'
        ]

    def create(self, validated_data):
        # Extract nested data
        refills_data = validated_data.pop('refills', [])
        deductions_data = validated_data.pop('deductions', [])
        referrals_data = validated_data.pop('referrals', [])

        # Create the user instance
        user = User.objects.create(**validated_data)

        # Create nested objects if provided
        for refill_data in refills_data:
            user.refills.create(**refill_data)

        for deduction_data in deductions_data:
            user.deductions.create(**deduction_data)

        for referral_data in referrals_data:
            referral_payments_data = referral_data.pop('referral_payments', [])
            referral = user.referrals.create(**referral_data)
            for payment_data in referral_payments_data:
                referral.referral_payments.create(**payment_data)

        return user

    def update(self, instance, validated_data):
        # Extract nested data
        refills_data = validated_data.pop('refills', [])
        deductions_data = validated_data.pop('deductions', [])
        referrals_data = validated_data.pop('referrals', [])

        # Update the user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nested objects
        if refills_data:
            instance.refills.all().delete()
            for refill_data in refills_data:
                instance.refills.create(**refill_data)

        if deductions_data:
            instance.deductions.all().delete()
            for deduction_data in deductions_data:
                instance.deductions.create(**deduction_data)

        if referrals_data:
            instance.referrals.all().delete()
            for referral_data in referrals_data:
                referral_payments_data = referral_data.pop('referral_payments', [])
                referral = instance.referrals.create(**referral_data)
                for payment_data in referral_payments_data:
                    referral.referral_payments.create(**payment_data)

        return instance

class UserListView(APIView):
    """
    Представление для списка пользователей и создания нового пользователя.
    """

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """
    Представление для работы с конкретным пользователем (чтение, обновление, удаление).
    """

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)  # `partial=True` позволяет обновлять частично
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
