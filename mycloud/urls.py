from django.urls import path
from . import views

urlpatterns = [
    path('api/account/', views.AccountListCreate.as_view() ),
    path('api/file/', views.FileModelListCreate.as_view() ),
]