from rest_framework.viewsets import ModelViewSet
from .serializer_new import NewSerializer
from rest_framework import generics
from .model_new import New


class NewListCreateView(generics.ListCreateAPIView):
    queryset = New.objects.all()
    serializer_class = NewSerializer

class NewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = New.objects.all()
    serializer_class = NewSerializer

class NewViewSet(ModelViewSet):
    queryset = New.objects.all()
    serializer_class = NewSerializer
