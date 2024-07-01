from datetime import date
import json

from django.http import FileResponse, JsonResponse
from django.db.models import Sum, Count
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from rest_framework.generics import CreateAPIView
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets

from .models import Account, FileModel, file_system
from .serializers import AccountSerializer, FileModelSerializer, RegistrationSerializer

# User views
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

# регистрация пользователя
class RegistrationView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data = request.data)
        data = {}

        if serializer.is_valid():
            serializer.save()
            data['response'] = True
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({
        'message': 'csrf cookies are ready'
        })

# вход пользователя в систему 
@permission_classes([IsAuthenticated])
@csrf_exempt
@api_view(['POST'])
def login_view(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')

    if email is None or password is None:
        return JsonResponse({
            'message': 'Введите логин и пароль'
        }, status=400)

    user = authenticate(email=email, password=password)

    if user is not None:
        login(request, user)

        return JsonResponse({
            'message': 'Вход выполнен',
        })
    
    return JsonResponse(
        {
        'message': 'Данные введены неверно'
        }, status=400
    )

# выход пользователя из системы 
@permission_classes([IsAuthenticated])
@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    logout(request)
    
    return JsonResponse({
        'message': 'Выход выполнен',
    })


def profile_view(request):
    data = request.user

    return JsonResponse({
        'username': data.username,
        'isAdmin': data.is_staff,
    })

# получение списка пользователей
@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAdminUser])
def get_detail_user_list(request):
    result = Account.objects.annotate(size=Sum('filemodel__size'), count=Count('filemodel__id')).values(
        'id', 'username', 'first_name', 'last_name', 'email', 'count', 'size', 'is_staff')

    if result:
        return Response(result, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_404_NOT_FOUND)

# удаление пользователя
@api_view(['DELETE'])
@csrf_exempt
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    user = Account.objects.get(id=user_id)
    if user:
        user.delete()
        return JsonResponse({
            'message': 'Пользователь удален',
        })
    return JsonResponse({
        'message': 'Пользователь не найден',
    }, status=404)
        

# File views

class FileModelView(generics.ListAPIView):
    serializer_class = FileModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self, user_id=None):

        if self.request.user.is_staff and user_id:
            return FileModel.objects.filter(user=user_id).all()

        return FileModel.objects.filter(user=self.request.user.id).all()
    
    # получение файлов
    def get(self, request):

        if 'id' not in request.query_params:
            user_id = None

            if 'user_id' in request.query_params:
                user_id = request.query_params['user_id']

            files = self.get_queryset(user_id).values('id', 'user__username', 'file_name', 'size', 'date_upload', 'date_last_download', 'comment')
            return Response(files)
        
        file = self.get_queryset().filter(id = request.query_params['id']).first()

        if file:
            file.date_last_download = date.today()
            file.save()
            return FileResponse(file.file, status.HTTP_200_OK, as_attachment=True)

        data = {
                'message': 'Файл не найден',
            }
        
        return Response(data, status=status.HTTP_404_NOT_FOUND)
    
    # загрузка файла в хранилище
    def post(self, request):
        serializer = FileModelSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            serializer.create(user_id=request.user.id, file=request.FILES['file'])

            data = self.get_queryset().values('id', 'user__username', 'file_name', 'size', 'date_upload', 'date_last_download', 'comment')
            
            return Response(data, status=status.HTTP_200_OK) 

        data = serializer.errors

        return Response(data)
    
    # переименование файла, изменение комментария к файлу
    def patch(self, request):
        serializer = FileModelSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            user = request.user

            serializer.patch(
                user=user,
            )

            if 'user_storage_id' in request.query_params and user.is_staff:
                data = self.get_queryset(
                    user_id=request.query_params['user_storage_id']
                ).values(
                    'id',
                    'user__username',
                    'file_name',
                    'size',
                    'date_upload',
                    'date_last_download',
                    'comment'
                )
            else:
                data = self.get_queryset().values(
                    'id',
                    'user__username',
                    'file_name',
                    'size',
                    'date_upload',
                    'date_last_download',
                    'comment'
                )

            return Response(data)

        data = serializer.errors
        
        return Response(data)
    
    # удаление файла из хранилища
    def delete(self, request):
        if request.user.is_staff:
            deleted_file = FileModel.objects.filter(
                id=int(request.query_params['id'])
            ).first()
        else:
            deleted_file = FileModel.objects.filter(
                user_id=request.user.id
            ).all().filter(
                id=int(request.query_params['id'])
            ).first()

        if deleted_file:
            file_system.delete(deleted_file.storage_file_name)

            deleted_file.delete()

            user = request.user

            if 'user_storage_id' in request.query_params and user.is_staff:
                data = self.get_queryset(
                    user_id=request.query_params['user_storage_id']
                ).values(
                    'id',
                    'user__username',
                    'file_name',
                    'size',
                    'date_upload',
                    'date_last_download',
                    'comment'
                )
            else:
                data = self.get_queryset().values(
                    'id',
                    'user__username',
                    'file_name',
                    'size',
                    'date_upload',
                    'date_last_download',
                    'comment'
                )
       
            return Response(data, status.HTTP_200_OK)

        data = {
            'message': 'Файл не найден',
        }
        
        return Response(data, status.HTTP_404_NOT_FOUND)

# формирование специальной ссылки на файл для использования внешними пользователями    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_external_file_path(request):
    user_id = request.user.id
    file_id = request.query_params['file_id']

    if request.user.is_staff:
        file = FileModel.objects.filter(id=file_id).first()
    else:
        file = FileModel.objects.filter(user_id=user_id).filter(id=file_id).first()
    
    if file:
        data = {
            'link': file.external_file_path,
        }

        return Response(data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_204_NO_CONTENT)

# скачивание файла через специальную ссылку, используемую внешними пользователями или веб-приложениями
@api_view(['GET'])
def get_file(request, link):
    file = FileModel.objects.filter(external_file_path=link).first()

    if file:
        file.date_last_download = date.today()
        file.save()
        
        return FileResponse(file.file_path, status.HTTP_200_OK, as_attachment=True, filename=file.file_name)

    return Response(status=status.HTTP_404_NOT_FOUND)
