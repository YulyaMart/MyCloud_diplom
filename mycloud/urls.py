from django.urls import path
from . import views

urlpatterns = [
    # path('api/account/', views.AccountListCreate.as_view() ),
    path('api/file/', views.FileModelListCreate.as_view() ),

    path('api/auth/login/', views.login_view),
    path('api/auth/logout/', views.logout_view),
    path('api/auth/get_csrf/', views.get_csrf_token),
    path('api/auth/profile/', views.profile_view),
    path('api/detail_users_list/', views.get_detail_user_list),
    path('api/delete_user/<int:user_id>/', views.delete_user),
    path('api/register/', views.RegistrationView.as_view()),
]