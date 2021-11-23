from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat, name='chat'),
    path('manage/online/', views.manageOnlineUsers, name="manageOnlineUsers")
]
