from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


# Модель пользователя
class AccountManager(BaseUserManager):
    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Укажите электронную почту')

        if not username:
            raise ValueError('Укажите имя пользователя')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self._create_user(email, username, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# Модель файла    

class FileModel(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Владелец файла')
    file_name = models.CharField(unique=True, max_length=50, verbose_name='Имя файла')
    size = models.BigIntegerField(null=True, verbose_name='Размер файла')
    date_upload = models.DateField(auto_now_add=True, null=True, verbose_name='Дата загрузки')
    date_last_download = models.DateField(null=True, verbose_name='Дата последнего скачивания')
    comment = models.TextField(max_length=500, null=True, blank=True, verbose_name='Комментарий')
    file_path = models.CharField(db_index=True, max_length=500, verbose_name="Путь к файлу")
    external_file_path = models.URLField(blank=True, verbose_name='Cсылка на файл')
    # file_path = models.FileField(upload_to=get_user_directory_path)
    
    def __str__(self):
        return self.file_name
