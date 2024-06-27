from django.shortcuts import render
from .models import Account, FileModel
from .serializers import AccountSerializer, FileModelSerializer
from rest_framework import generics

class AccountListCreate(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class FileModelListCreate(generics.ListAPIView):
    queryset = FileModel.objects.all()
    serializer_class = FileModelSerializer