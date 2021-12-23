from django.contrib.auth import login
from django.shortcuts import redirect, render

# Create your views here.
import uuid
from django.core.cache import cache
from .utils import Response
from .constants import *
from .service import add_remove_online_user, updateLocationList
from django.contrib.auth.decorators import login_required

import uuid

def home(request):
    return render(request, "app/home.html")

@login_required
def startRoom(request):
    room_id = str(uuid.uuid4())[0]
    return redirect("app:enterRoom", room_id=room_id)

@login_required
def enterRoom(request, room_id):
    user_unique_id = request.user.user_profile.unique_id
    online_users = cache.get('online_users')
    if not online_users:
        online_users = set()

    context = {
        "username" : user_unique_id,
        "online_users" : online_users,
        "room_id" : room_id
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
