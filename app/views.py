from django.shortcuts import render

# Create your views here.
import uuid
from django.core.cache import cache
from .utils import Response
from .constants import *
from .service import add_remove_online_user
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "app/home.html")

@login_required
def chat(request):
    unique_id = request.user.user_profile.unique_id
    online_users = cache.get('online_users')
    if not online_users:
        online_users = set()

    context = {
        "username" : unique_id,
        "online_users" : online_users
    }
    return render(request, "app/index.html", context=context)

def manageOnlineUsers(request):
    if request.method == "POST":
        print("[ manageOnlineUsers ]")
        action = request.POST.get("action")
        username = request.POST.get("username")

        online_users = add_remove_online_user(action, username)
        if not online_users:
            return Response(FAILED, "Invalid action provided", status=400)
        
        return Response(SUCCESS, action+" action performed for "+username, data=online_users)

        
    