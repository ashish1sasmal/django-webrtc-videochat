from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path('', views.home, name='home'),
    path('start/chat/', views.startRoom, name='startRoom'),
    path('chat/<str:room_id>', views.enterRoom, name='enterRoom'),
    path('manage/online/', views.manageOnlineUsers, name="manageOnlineUsers"),
    path('location/update/', views.locationSharing, name="locationSharing"),
    path('lobby/<str:room_id>', views.waitRoom, name="waitRoom"),
    path('chat/response/', views.roomResponse, name='roomResponse',),
    path("sendInvite/", views.sendInvite, name="sendInvite"),
    path('delete/room/<str:room_id>', views.deleteRoom, name="deleteRoom"),
    path("chatroom", views.chatroom, name="chatroom")
]
