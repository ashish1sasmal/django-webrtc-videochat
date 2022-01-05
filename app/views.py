from django.contrib.auth import login
from django.http.response import HttpResponse
from django.shortcuts import redirect, render

# Create your views here.
import uuid
from django.core.cache import cache

from app.models import ChatRoom, Message
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
from .email import emailSend
import os
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count

channel_layer = get_channel_layer()

def home(request):
    if request.method == "GET":
        context = {}
        if request.user.is_authenticated:
            rooms = ChatRoom.objects.filter(members__in=[request.user]).order_by("-last_active")
            context={
                "rooms": rooms
            }
        return render(request, "app/home.html", context)
    else:
        room_id = request.POST.get("room_id")
        try:
            room = ChatRoom.objects.get(room_id=room_id)
            return redirect("app:enterRoom", room_id=room_id)
        except Exception as err:
            print(str(err)+ " home "+room_id)
            context = {}
            if request.user.is_authenticated:
                rooms = ChatRoom.objects.filter(members__in=[request.user]).order_by("-last_active")[:3]
                context={
                    "rooms": rooms
                }
            return render(request, "app/home.html", context)

@login_required
def startRoom(request):
    room_id = str(uuid.uuid4().hex)[:8]
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
            "room": room,
            "messages": room.message_room.all()
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


def sendInvite(request):
    email = request.GET.get("email")
    room_id = request.GET.get("room_id")
    try:
        print(f"room_id : {room_id}")
        room = ChatRoom.objects.get(room_id=room_id)
        msg = f"""
        <div>
            <h4><b>Host : {room.admin}</b></h4>
            <h4><b>Join using <a href="{os.environ.get('HOST')}/chat/{room_id}">Link</a></b></h4>
        </div>
        """
        send = emailSend("Video Call Invite", msg, [email])
        if send:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})
    except ChatRoom.DoesNotExist as err:
        print(str(err))
        return JsonResponse({"success": False})
    
@login_required
def deleteRoom(request, room_id):
    try:
        room = ChatRoom.objects.get(room_id=room_id)
        room.delete()
        return JsonResponse({"result": True})
    except Exception as err:
        print(str(err))
        return JsonResponse({"result": False})

@login_required
def chatroom(request):
    try:
        user_id = request.GET.get("user")
        print(user_id)
        user = User.objects.get(user_profile__unique_id=user_id)
        room = None
        try:
            print(request.user, user)
            room = ChatRoom.objects.annotate(c=Count("members")).filter(c=2,members__in = (request.user,)).get(members__in = (user,))
        except ChatRoom.DoesNotExist as err:
            print(str(err))
            room = ChatRoom(admin=request.user, room_id=str(uuid.uuid4())[:8])
            room.save()
            room.members.add(request.user)
            room.members.add(user)
            room.save()
        other_user = None
        for i in room.members.all():
            if i!=request.user:
                other_user = i
                break
        messages = room.message_room.all()
        return render(request, "app/chatroom.html", {"messages": messages, "room":room, "other": other_user})
    except Exception as err:
        print(str(err))
        return HttpResponse("<h4><b>Error occurred</b></h4>")