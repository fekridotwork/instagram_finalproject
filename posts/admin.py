from django.contrib import admin
from .models import Post, Story, Hashtag, PostHashtag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "media_type",
        "visibility",
        "is_deleted",
        "likes_count",
        "comments_count",
        "created_at",
    )
    search_fields = ("user__username", "user__email", "caption")
    list_filter = ("media_type", "visibility", "is_deleted", "is_edited")
    ordering = ("-created_at",)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "media_type",
        "visibility",
        "is_deleted",
        "expires_at",
        "created_at",
    )
    search_fields = ("user__username", "user__email", "text")
    list_filter = ("media_type", "visibility", "is_deleted")
    ordering = ("-created_at",)


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "hashtag", "created_at")
    search_fields = ("hashtag__name", "post__user__username", "post__user__email")
    ordering = ("-created_at",)