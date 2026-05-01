from django.contrib import admin
from .models import Post, Story, Hashtag, PostHashtag

from django.db.models import Count
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "media_type",
        "visibility",
        "is_deleted",
        "likes_count_display",
        "comments_count",
        "created_at",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            calculated_likes_count=Count("received_likes")
        )
    def likes_count_display(self, obj):
        return obj.calculated_likes_count

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