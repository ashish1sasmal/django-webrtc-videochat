from django.contrib import admin

# Register your models here.
from app.models import ChatRoom, Message

admin.site.register(ChatRoom)
admin.site.register(Message)