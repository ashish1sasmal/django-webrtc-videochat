from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('logout/', views.user_logout, name="logout"),
    path('register/', views.registerView, name='registerView'),
    path('api/register/', views.register, name='register'),
    path('login/', views.loginView, name="loginView"),
    path("api/login/", views.user_login, name="login")
]
