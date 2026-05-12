from rest_framework import serializers

from accounts.models import User
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user_id',
            'username',
            'post',
            'parent',
            'text',
            'is_deleted',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = [
            'id',
            'user_id',
            'username',
            'post',
            'is_deleted',
            'created_at',
            'updated_at',
        ]

    def get_replies(self, obj):
        replies = obj.replies.filter(is_deleted=False)
        return CommentSerializer(replies, many=True).data

    def validate_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Comment cannot be empty."
            )

        if len(value) > 500:
            raise serializers.ValidationError(
                "Comment cannot be longer than 500 characters."
            )

        return value
    
class FollowUserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(
        source="profile.display_name",
        read_only=True,
    )
    profile_image = serializers.ImageField(
        source="profile.profile_image",
        read_only=True,
    )
    is_private = serializers.BooleanField(
        source="profile.is_private",
        read_only=True,
    )

    # followers_count = serializers.IntegerField(read_only=True)
    # following_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "profile_image",
            "username",
            "display_name",
            "is_private",
        ]