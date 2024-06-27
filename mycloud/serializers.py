from rest_framework import serializers
from .models import FileModel, Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_active')

class FileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = ('id', 'user', 'file_name', 'size', 'date_upload', 'date_last_download', 'comment', 'file_path', 'external_file_path')
        