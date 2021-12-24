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

def home(request):
    if request.user.is_authenticated:
        rooms = ChatRoom.objects.filter(members__in=[request.user])
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
def enterRoom(request, room_id):
    room = ChatRoom.objects.get(room_id=room_id)
    context = {
        "room": room
    }
    return render(request, "app/sender2.html", context=context)

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
