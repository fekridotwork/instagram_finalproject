from drf_spectacular.utils import extend_schema_view
from django.db.models import Count, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from interactions.services import exclude_blocked_conversations, is_blocked_between

from .models import DirectConversation, DirectMessage
from .schemas import (
    conversation_create_schema,
    conversation_list_schema,
    conversation_message_create_schema,
    conversation_messages_list_schema,
    direct_message_delete_schema,
    direct_message_update_schema,
)
from .serializers import (
    ConversationSerializer,
    DirectMessageSerializer,
    DirectMessageUpdateSerializer,
    InboxConversationSerializer,
    StartConversationSerializer,
)


@extend_schema_view(
    get=conversation_list_schema,
    post=conversation_create_schema,
)
class ConversationListCreateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StartConversationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user_id = serializer.validated_data["user_id"]
        target_user = User.objects.get(id=target_user_id)

        if is_blocked_between(request.user, target_user):
            self.permission_denied(
                request,
                message="You cannot start a conversation with this user.",
            )

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
        last_message_queryset = (
            DirectMessage.objects
            .filter(conversation=OuterRef("pk"))
            .order_by("-created_at")
        )

        conversations = exclude_blocked_conversations(
            DirectConversation.objects
            .filter(Q(user1=request.user) | Q(user2=request.user))
            .select_related(
                "user1",
                "user1__profile",
                "user2",
                "user2__profile",
            )
            .annotate(
                messages_count=Count("messages"),
                last_message=Subquery(
                    last_message_queryset.values("text")[:1]
                ),
                last_message_sender_id=Subquery(
                    last_message_queryset.values("sender_id")[:1]
                ),
                last_message_created_at=Subquery(
                    last_message_queryset.values("created_at")[:1]
                ),
            )
            .filter(messages_count__gt=0)
            .order_by("-updated_at"),
            request.user,
        )

        following_ids = set(
            request.user.following_relations.values_list(
                "following_id",
                flat=True,
            )
        )

        page = self.paginate_queryset(conversations)

        if page is not None:
            serializer = InboxConversationSerializer(
                page,
                many=True,
                context={
                    "request": request,
                    "following_ids": following_ids,
                },
            )
            return self.get_paginated_response(serializer.data)

        serializer = InboxConversationSerializer(
            conversations,
            many=True,
            context={
                "request": request,
                "following_ids": following_ids,
            },
        )
        return Response(serializer.data)


@extend_schema_view(
    get=conversation_messages_list_schema,
    post=conversation_message_create_schema,
)
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

        other_user = (
            conversation.user2
            if conversation.user1 == request.user
            else conversation.user1
        )

        if is_blocked_between(request.user, other_user):
            self.permission_denied(
                request,
                message="You cannot view messages with this user.",
            )

        messages = (
            DirectMessage.objects
            .filter(conversation=conversation)
            .select_related("sender")
            .order_by("created_at")
        )

        page = self.paginate_queryset(messages)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        conversation = self.get_conversation()

        other_user = (
            conversation.user2
            if conversation.user1 == request.user
            else conversation.user1
        )

        if is_blocked_between(request.user, other_user):
            self.permission_denied(
                request,
                message="You cannot send messages to this user.",
            )

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
    

@extend_schema_view(
    patch=direct_message_update_schema,
    delete=direct_message_delete_schema,
)
class DirectMessageDetailAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DirectMessageUpdateSerializer

    def get_message(self):
        return get_object_or_404(
            DirectMessage.objects.select_related(
                "conversation",
                "conversation__user1",
                "conversation__user2",
            ),
            Q(conversation__user1=self.request.user) |
            Q(conversation__user2=self.request.user),
            id=self.kwargs["message_id"],
        )

    def patch(self, request, message_id):
        message = self.get_message()

        if message.sender != request.user:
            self.permission_denied(
                request,
                message="You can only edit your own messages.",
            )

        serializer = self.get_serializer(
            message,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = DirectMessageSerializer(message)
        return Response(response_serializer.data)

    def delete(self, request, message_id):
        message = self.get_message()

        if message.sender != request.user:
            self.permission_denied(
                request,
                message="You can only delete your own messages.",
            )

        conversation = message.conversation
        message.delete()

        last_message = conversation.messages.order_by("-created_at").first()

        if last_message:
            conversation.updated_at = last_message.created_at
        else:
            conversation.updated_at = conversation.created_at

        conversation.save(update_fields=["updated_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)