from .payment_serializer import PaymentAccountSerializer, RefillSerializer, DeductionSerializer
from .payment_model import PaymentAccount, Refill, Deduction
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins


class PaymentAccountViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = PaymentAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только платёжные аккаунты текущего авторизованного пользователя.
        """
        return PaymentAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        # Проверяем, существует ли уже платёжный аккаунт для пользователя
        if PaymentAccount.objects.filter(user=user).exists():
            raise ValidationError("Платёжный аккаунт для данного пользователя уже существует.")

        # Создаем новый платёжный аккаунт
        serializer.save(user_id=user.id)

    @action(detail=True, methods=['get'])
    def refills(self, request, pk=None):
        """
        Возвращает список пополнений для указанного платёжного аккаунта.
        """
        account = self.get_object()
        refills = account.refills.all()
        serializer = RefillSerializer(refills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def deductions(self, request, pk=None):
        """
        Возвращает список списаний для указанного платёжного аккаунта.
        """
        account = self.get_object()
        deductions = account.deductions.all()
        serializer = DeductionSerializer(deductions, many=True)
        return Response(serializer.data)


class RefillViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    queryset = Refill.objects.all()
    serializer_class = RefillSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Создает новое пополнение и увеличивает баланс соответствующего аккаунта.
        """
        # Получаем аккаунт по account_id из запроса
        account = PaymentAccount.objects.get(account_id=self.kwargs['account_id'])

        # Увеличиваем баланс
        account.balance += serializer.validated_data['amount']
        account.save()

        # Сохраняем объект пополнения, связанный с аккаунтом
        serializer.save(account=account)


class DeductionViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        account = PaymentAccount.objects.get(account_id=self.kwargs['account_id'])
        serializer.save(account=account)

# ##from .payment_forms import PaymentAccountForm, RefillForm, DeductionForm
# from django.shortcuts import render, get_object_or_404, redirect
# # Представление для списка платёжных аккаунтов
# def payment_account_list(request):
#     accounts = PaymentAccount.objects.all()
#     return render(request, 'payment_account_list.html', {'accounts': accounts})
#
# # Представление для создания нового платёжного аккаунта
# def payment_account_create(request):
#     if request.method == 'POST':
#         form = PaymentAccountForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('payment_account_list')
#     else:
#         form = PaymentAccountForm()
#     return render(request, 'payment_account_form.html', {'form': form})
#
# # Представление для детальной информации о платёжном аккаунте
# def payment_account_detail(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     return render(request, 'payment_account_detail.html', {'account': account})
#
# # Представление для редактирования платёжного аккаунта
# def payment_account_edit(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     if request.method == 'POST':
#         form = PaymentAccountForm(request.POST, instance=account)
#         if form.is_valid():
#             form.save()
#             return redirect('payment_account_list')
#     else:
#         form = PaymentAccountForm(instance=account)
#     return render(request, 'payment_account_form.html', {'form': form})
#
# # Представление для удаления платёжного аккаунта
# def payment_account_delete(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     account.delete()
#     return redirect('payment_account_list')
#
# # Представление для пополнений
# def refill_list(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     refills = account.refills.all()
#     return render(request, 'refill_list.html', {'account': account, 'refills': refills})
#
# # Представление для создания нового пополнения
# def refill_create(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     if request.method == 'POST':
#         form = RefillForm(request.POST)
#         if form.is_valid():
#             refill = form.save(commit=False)
#             refill.account = account
#             refill.save()
#             return redirect('refill_list', account_id=account_id)
#     else:
#         form = RefillForm()
#     return render(request, 'refill_form.html', {'form': form, 'account': account})
#
# # Представление для списаний
# def deduction_list(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     deductions = account.deductions.all()
#     return render(request, 'deduction_list.html', {'account': account, 'deductions': deductions})
#
# # Представление для создания нового списания
# def deduction_create(request, account_id):
#     account = get_object_or_404(PaymentAccount, pk=account_id)
#     if request.method == 'POST':
#         form = DeductionForm(request.POST)
#         if form.is_valid():
#             deduction = form.save(commit=False)
#             deduction.account = account
#             deduction.save()
#             return redirect('deduction_list', account_id=account_id)
#     else:
#         form = DeductionForm()
#     return render(request, 'deduction_form.html', {'form': form, 'account': account})
