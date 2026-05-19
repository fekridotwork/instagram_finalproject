from rest_framework import serializers

from accounts.models import User
from interactions.serializers import FollowUserSerializer
from .models import DirectConversation, DirectMessage



class StartConversationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("User not found.")

        if self.context["request"].user.id == value:
            raise serializers.ValidationError(
                "You cannot start a conversation with yourself."
            )
        return value
    
class ConversationSerializer(serializers.ModelSerializer):
    user1_id = serializers.IntegerField(
        source="user1.id",
        read_only=True,
    )
    user2_id = serializers.IntegerField(
        source="user2.id",
        read_only=True,
    )

    class Meta:
        model = DirectConversation
        fields = [
            "id",
            "user1_id",
            "user2_id",
            "created_at",
            "updated_at",
        ]
    
class DirectMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(
        source="sender.id",
        read_only=True,
    )

    class Meta:
        model = DirectMessage
        fields = [
            "id",
            "sender_id",
            "text",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sender_id",
            "created_at",
        ]
    
class InboxConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()

    last_message = serializers.CharField(read_only=True)
    last_message_sender_id = serializers.IntegerField(read_only=True)
    last_message_created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = DirectConversation
        fields = [
            "id",
            "other_user",
            "updated_at",
            "last_message",
            "last_message_sender_id",
            "last_message_created_at",
        ]

    def get_other_user(self, obj):
        request_user = self.context["request"].user

        if obj.user1 == request_user:
            other_user = obj.user2
        else:
            other_user = obj.user1

        return FollowUserSerializer(other_user).data
    
    