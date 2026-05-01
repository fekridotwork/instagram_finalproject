from rest_framework import serializers

from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

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