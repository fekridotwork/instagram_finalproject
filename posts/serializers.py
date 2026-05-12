from rest_framework import serializers
from interactions.serializers import CommentSerializer
from .models import Post, Story


class PostSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "user_id",
            "username",
            "media",
            "media_type",
            "caption",
            "visibility",
            "likes_count",
            "comments_count",
            "is_deleted",
            "is_edited",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_deleted",
            "is_edited",
            "created_at",
            "updated_at",
        ]
class PostListSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = [
            "id",
            "user_id",
            "username",
            "media",
            "media_type",
            "caption",
            "likes_count",
            "comments_count",
            "created_at",
        ]


class PostDetailSerializer(PostSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            "comments",
        ]

    def get_comments(self, obj):
        comments = (
            obj.comments
            .filter(parent__isnull=True, is_deleted=False)
            .select_related("user")
            .prefetch_related("replies")
        )
        return CommentSerializer(comments, many=True).data

class StorySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Story
        fields = [
            "id",
            "user_id",
            "username",
            "media",
            "media_type",
            "text",
            "visibility",
            "is_deleted",
            "expires_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "username",
            "is_deleted",
            "expires_at",
            "created_at",
        ]