from rest_framework import serializers

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