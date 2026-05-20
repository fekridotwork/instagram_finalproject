from django.db.models import Prefetch
from rest_framework import serializers

from interactions.models import Comment
from interactions.serializers import CommentSerializer
from posts.services.media_validation import validate_media_file

from .models import Post, Story


class PostSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    is_liked = serializers.BooleanField(read_only=True)
    is_saved = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        media = attrs.get("media")
        media_type = attrs.get("media_type")

        if self.instance is None:
            if not media:
                raise serializers.ValidationError(
                    {"media": "Media is required."}
                )

            if not media_type:
                raise serializers.ValidationError(
                    {"media_type": "Media type is required."}
                )

            validate_media_file(media, media_type)
            return attrs

        if media is not None:
            final_media_type = media_type or self.instance.media_type
            validate_media_file(media, final_media_type)

        return attrs


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
            "is_liked",
            "is_saved",
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
    def validate_caption(self, value):
        if value is None:
            return value

        value = value.strip()

        if len(value) > 2200:
            raise serializers.ValidationError(
                "Caption is too long."
            )

        return value


class PostListSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
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
            "is_liked",
            "is_saved",
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
            .prefetch_related(
                Prefetch(
                    "replies",
                    queryset=Comment.objects
                    .filter(is_deleted=False)
                    .select_related("user")
                    .order_by("created_at"),
                    to_attr="prefetched_replies",
                )
            )
        )
        return CommentSerializer(comments, many=True).data

class StorySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    def validate_text(self, value):
        if value is None:
            return value
        
        value = value.strip()

        if len(value) > 500:
            raise serializers.ValidationError(
                "Story text is too long."
            )
        return value
    

    def validate(self, attrs):
        media = attrs.get("media", getattr(self.instance, "media", None))
        media_type = attrs.get(
            "media_type",
            getattr(self.instance, "media_type", None),
        )
        text = attrs.get("text", getattr(self.instance, "text", ""))

        if isinstance(text, str):
            text = text.strip()

        if media_type == "text":
            if media:
                raise serializers.ValidationError(
                    {
                        "media": "Text stories cannot have media."
                    }
                )

            if not text:
                raise serializers.ValidationError(
                    {
                        "text": "Text story cannot be empty."
                    }
                )

        elif media_type in {"image", "video"}:
            if not media:
                raise serializers.ValidationError(
                    {
                        "media": "Media is required for image/video stories."
                    }
                )

            validate_media_file(media, media_type)

        else:
            raise serializers.ValidationError(
                {
                    "media_type": "Invalid story type."
                }
            )

        attrs["text"] = text
        return attrs
    
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