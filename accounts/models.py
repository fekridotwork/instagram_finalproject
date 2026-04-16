from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    is_email_verified = models.BooleanField(
        default=False,
    )
    is_phone_verified = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.email or self.phone_number or self.username