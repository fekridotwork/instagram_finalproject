from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

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
            "is_deleted",
            "is_edited",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "is_deleted",
            "is_edited",
            "created_at",
            "updated_at",
        ]
