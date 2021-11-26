from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path('', views.home, name='home'),
    path('start/chat/', views.startRoom, name='startRoom'),
    path('chat/<str:room_id>', views.enterRoom, name='enterRoom'),
    path('manage/online/', views.manageOnlineUsers, name="manageOnlineUsers"),
    path('location/update/', views.locationSharing, name="locationSharing")
]
