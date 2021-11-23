from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
User = get_user_model()

import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="user_profile", on_delete=models.CASCADE)
    last_login = models.DateTimeField(blank=True, null=True)
    unique_id = models.CharField(max_length=8, default=str(uuid.uuid4())[:8])
    email_confirm = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username