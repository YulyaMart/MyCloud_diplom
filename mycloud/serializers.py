from rest_framework import serializers
from django.core.files import File

from mycloud.file_model_patch_validator import patchValidator
from mycloud.generate_external_link import generate_external_link_key
from .models import FileModel, Account

# User serializers

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

# File serializers

class FileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = ('id', 'user', 'file_name', 'size', 'date_upload', 'date_last_download', 'comment', 'file_path', 'external_file_path')
    
    def create(self, **kwargs):

        file = File(self.validated_data['file'])
        user = Account.objects.filter(id=kwargs['user_id']).first()

        data = {
            'user': user,
            'file_name': file.name,
            'size': file.size,
            'comment': self.validated_data['comment'],
            'file_path': file,
            'external_file_path': generate_external_link_key(),
        }
        
        try:
            file_model = FileModel.objects.create(**data)

            return file_model

        except Exception as e:
            error = {
                'message': ', '.join(e.args) if len(e.args) > 0 else 'Unknown Error'
            }
            
            raise serializers.ValidationError(error)

    def patch(self, **kwargs):

        validated_data = patchValidator(self.initial_data)

        if kwargs['user'].is_staff:
            file = FileModel.objects.filter(id=validated_data['id']).first()
        else:
            file = FileModel.objects.filter(user_id=kwargs['user'].id).filter(id=validated_data['id']).first()

        if file:
            file.comment = validated_data['comment']

            return file.save()