from django.contrib.auth import login
from django.shortcuts import redirect, render

# Create your views here.
import uuid
from django.core.cache import cache

from app.models import ChatRoom
from .utils import Response
from .constants import *
from .service import add_remove_online_user, updateLocationList
from django.contrib.auth.decorators import login_required

import uuid
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from user.models import Profile

channel_layer = get_channel_layer()

def home(request):
    context = {}
    if request.user.is_authenticated:
        rooms = ChatRoom.objects.filter(members__in=[request.user]).order_by("-last_active")[:3]
        context={
            "rooms": rooms
        }
    return render(request, "app/home.html", context)

@login_required
def startRoom(request):
    room_id = str(uuid.uuid4())[:8]
    room = ChatRoom(admin=request.user, room_id=room_id)
    room.save()
    room.members.add(request.user)
    room.save()
    print("[ Chatroom created ]")
    return redirect("app:enterRoom", room_id=room_id)

@login_required
def waitRoom(request, room_id):
    room = ChatRoom.objects.get(room_id=room_id)
    msg = {
        "type" : "join_request",
        "user" : {"id": request.user.user_profile.unique_id, "name": request.user.username
        },
        "to" : room.admin.user_profile.unique_id
    }
    print(msg, "request sent", room.room_id)
    async_to_sync(channel_layer.group_send)(room.room_id ,msg)
    return render(request, "app/waitroom.html", {"room":room})

@login_required
def roomResponse(request):
    print("hello", request.GET)
    room_id = request.GET.get("roomid")
    userid = request.GET.get("userid")
    resp = request.GET.get("resp")
    try:
        room = ChatRoom.objects.get(room_id=room_id)
        if request.user == room.admin:
            msg = {
                "response": resp,
                "type": "room_request",
                "room_id": room.room_id
            }
            if resp == "accept":
                user = Profile.objects.get(unique_id=userid)
                room.members.add(user.user)
                room.save()
            async_to_sync(channel_layer.group_send)(userid ,msg)
    except Exception as err:
        print(str(err))
    return JsonResponse({})

@login_required
def enterRoom(request, room_id):
    try:
        print(f"room_id : {room_id}")
        room = ChatRoom.objects.get(room_id=room_id)
        if request.user not in room.members.all():
            return redirect("app:waitRoom", room_id=room_id)
        room.members.add(request.user)
        room.last_active = datetime.now()
        room.save()
        context = {
            "room": room
        }
        return render(request, "app/sender2.html", context=context)
    except ChatRoom.DoesNotExist as err:
        print(str(err))
        return JsonResponse({})

def locationSharing(request):
    latitude = request.GET.get("lat")
    longitude = request.GET.get("long")
    action = request.GET.get("action")
    username = request.GET.get("username")
    location_sharing_users = updateLocationList(action, username, latitude=latitude, longitude=longitude)
    if location_sharing_users == False:
        return Response("failed", "Invalid action provided", status=400)
    return Response("success", f"{action} performed", data=location_sharing_users)

def manageOnlineUsers(request):
    if request.method == "POST":
        print("[ manageOnlineUsers ]")
        action = request.POST.get("action")
        username = request.POST.get("username")

        online_users = add_remove_online_user(action, username)
        if not online_users:
            return Response(FAILED, "Invalid action provided", status=400)
        
        return Response(SUCCESS, action+" action performed for "+username, data=online_users)
