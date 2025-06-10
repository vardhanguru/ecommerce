from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=17)
    is_email_verified = models.BooleanField(default=False)


class EmailOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
