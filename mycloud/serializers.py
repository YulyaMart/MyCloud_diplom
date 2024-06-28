from rest_framework import serializers
from .models import FileModel, Account

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2']

    def save(self):
        user = Account(
            email = self.validated_data['email'],
            username = self.validated_data['username'],
            first_name = self.validated_data['first_name'],
            last_name = self.validated_data['last_name']
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({
                password: 'password does not match',
            })

        user.set_password(password)

        user.save()

        return user

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')


class FileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = ('id', 'user', 'file_name', 'size', 'date_upload', 'date_last_download', 'comment', 'file_path', 'external_file_path')
