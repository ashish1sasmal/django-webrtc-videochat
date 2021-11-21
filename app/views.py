from django.shortcuts import render

# Create your views here.
import uuid

def main(request):
    unique_id = str(uuid.uuid4())[:1]
    context = {
        "username" : unique_id
    }
    return render(request, "app/home.html", context=context)