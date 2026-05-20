from django.contrib import admin

from .models import DirectConversation, DirectMessage


@admin.register(DirectConversation)
class DirectConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "created_at", "updated_at")
    search_fields = (
        "user1__username",
        "user1__email",
        "user2__username",
        "user2__email",
    )
    ordering = ("-updated_at",)


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at")
    search_fields = (
        "sender__username",
        "sender__email",
        "conversation__user1__username",
        "conversation__user2__username",
    )
    ordering = ("-created_at",)