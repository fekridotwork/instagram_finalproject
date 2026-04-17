from django.contrib import admin
from .models import Follow, Like, Comment, SavePost


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = (
        "follower__username",
        "follower__email",
        "following__username",
        "following__email",
    )
    ordering = ("-created_at",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "post__user__username",
        "post__user__email",
    )
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "parent", "is_deleted", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "post__user__username",
        "post__user__email",
        "text",
    )
    list_filter = ("is_deleted",)
    ordering = ("-created_at",)


@admin.register(SavePost)
class SavePostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "post__user__username",
        "post__user__email",
    )
    ordering = ("-created_at",)