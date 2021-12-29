from django.shortcuts import render,redirect
from app.utils import Response
from django.contrib.auth import login,logout
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from datetime import datetime
from django.db.models import Count, Q
from django.http import JsonResponse
# Create your views here.

@login_required
def user_logout(request):
    logout(request)
    return redirect('app:home')

def registerView(request):
    return render(request, "user/register.html")

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        user_count = User.objects.filter(email=email).count()
        if user_count == 0:
            if password1 == password2:
                user = User(username=email, email=email)
                print(email,password1)
                user.set_password(password1)
                user.save()
                profile = Profile(user=user)
                profile.save()
                login(request,user)
                print(email + " registered")
                return Response("success", "registered successfully", status=200)
            else:
                return Response("failed", "password do not matched", status=400)
        else:
            return Response("failed", "User already exist", status=400)

def loginView(request):
    return render(request, "user/login.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user=authenticate(username=email,password=password)
        print(user)
        if user:
            user_profile = user.user_profile
            user_profile.last_login = datetime.now()
            user_profile.save()
            login(request, user)
            print(user.username + " logged in")
            return Response("success", "successfully logged in", status=200)
        else:
            print("Wrong credentials")
            return Response("failed", "login failed", status=400)

def profile(request, id):
    if request.method == "POST":
        data = request.POST
        name = data.get("user_name")
        email = data.get("email")
        mobile = data.get("user_mobile")
        address = data.get("user_address")
        bio = data.get("user_bio")
        user = request.user
        user.first_name = name
        user.save()
        profile = user.user_profile
        profile.mobile = mobile
        profile.bio = bio
        profile.address = address
        profile.save()
    try:
        profile = Profile.objects.get(unique_id=id)
    except Exception as err:
        return render(request, "app/home.html")
    return render(request, "user/profile.html", context={"profile": profile})


@login_required
def autocomplete(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        profiles = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query))
        results = []
        # ext = ChatGroup.objects.annotate(c=Count('members')).filter(c=2,members__in=[request.user])
        for profile in profiles:
            results.append({
                "label":profile.first_name if profile.first_name else profile.username,
                "value":profile.user_profile.unique_id
                })
        if results==[]:
            results.append({"label":"No Match Found","value":""})
        return JsonResponse(results,safe=False)

    # elif request.method=="GET":
    #     code = request.GET.get("mysearchid")
    #     group = ChatGroup.objects.get(code = code)
    #     return redirect("chat:room" ,room_code=code)


@login_required
def follow_user(request):
    print(request.GET)
    try:
        id = request.GET.get("id")
        action = request.GET.get("action")
        user = User.objects.get(user_profile__unique_id=id)
        print(user, id, action)
        profile = request.user.user_profile
        if action == "follow":
            print("hello")
            profile.follow.add(user)
            profile.save()
            return JsonResponse({"result":True})
        elif action == "unfollow":
            profile.follow.remove(user)
            profile.save()
            return JsonResponse({"result":True})
        else:
            return JsonResponse({"result":False})
    except Exception as err:
        print(str(err))
        return JsonResponse({"result":False})