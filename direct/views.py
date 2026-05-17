from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import User
from .models import DirectConversation, DirectMessage
from .serializers import (
    StartConversationSerializer,
    ConversationSerializer,
    InboxConversationSerializer,
    DirectMessageSerializer,
)

class ConversationListCreateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StartConversationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user_id = serializer.validated_data["user_id"]
        target_user = User.objects.get(id=target_user_id)

        user1, user2 = sorted(
            [request.user, target_user],
            key=lambda user: user.id,
        )

        conversation, created = DirectConversation.objects.get_or_create(
            user1 = user1,
            user2 = user2,
        )

        response_serializer = ConversationSerializer(conversation)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
    def get(self, request):
        conversations = (
            DirectConversation.objects
            .filter(Q(user1=request.user) | Q(user2=request.user))
            .select_related("user1", "user2")
            .order_by("-updated_at")
        )

        serializer = InboxConversationSerializer(
            conversations,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
    
class ConversationMessagesAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DirectMessageSerializer

    def get_conversation(self):
        return get_object_or_404(
            DirectConversation,
            Q(user1=self.request.user) | Q(user2=self.request.user),
            id=self.kwargs["conversation_id"],
        )

    def get(self, request, conversation_id):
        conversation = self.get_conversation()

        messages = (
            DirectMessage.objects
            .filter(conversation=conversation)
            .select_related("sender")
            .order_by("created_at")
        )

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        conversation = self.get_conversation()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.save(
            conversation=conversation,
            sender=request.user,
        )

        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])

        response_serializer = self.get_serializer(message)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )