from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    organization = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đơn vị/Tổ chức")

    def __str__(self):
        return f"{self.username} ({self.organization or 'No Org'})"
