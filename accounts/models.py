from email.policy import default

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

class Profile(models.Model):
    user = models.OneToOneField(
        "accounts.User",
        on_delete= models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(
        max_length=100,
    )
    display_name = models.CharField(
        max_length=50,
    )
    bio = models.TextField(
        blank=True,
        null=True,
    )
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )
    is_private = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return self.display_name or self.full_name or str(self.user)

class OTP(models.Model):
    PURPOSE_CHOICES = [
        ("register", "Register"),
        ("login", "Login"),
    ]
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="otps",
        null=True,
        blank=True,
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )
    code = models.CharField(
        max_length=6,
    )
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
    )
    is_used = models.BooleanField(
        default=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.purpose} - OTP"