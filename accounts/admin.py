from django.contrib import admin
from .models import User, Profile, OTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "phone_number",
        "is_active",
        "is_staff",
    )
    search_fields = ("username", "email", "phone_number")
    list_filter = ("is_active", "is_staff", "is_email_verified", "is_phone_verified")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "display_name",
        "is_private",
        "created_at",
    )
    search_fields = ("full_name", "display_name", "user__username", "user__email")
    list_filter = ("is_private",)
    ordering = ("-created_at",)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "email",
        "phone_number",
        "purpose",
        "is_used",
        "expires_at",
        "created_at",
    )
    search_fields = ("email", "phone_number", "user__username", "user__email", "code")
    list_filter = ("purpose", "is_used")
    ordering = ("-created_at",)