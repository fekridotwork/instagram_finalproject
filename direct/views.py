from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from interactions.services import is_blocked_between

from .models import DirectConversation, DirectMessage
from .serializers import (ConversationSerializer, DirectMessageSerializer,
                          InboxConversationSerializer,
                          StartConversationSerializer)


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

        conversations = (
            DirectConversation.objects
            .filter(Q(user1=request.user) | Q(user2=request.user))
            .exclude(
                user1__in=request.user.blocking_relations.values("blocked_id")
            )
            .exclude(
                user2__in=request.user.blocking_relations.values("blocked_id")
            )
            .exclude(
                user1__in=request.user.blocked_by_relations.values("blocker_id")
            )
            .exclude(
                user2__in=request.user.blocked_by_relations.values("blocker_id")
            )
            .select_related(
                "user1",
                "user1__profile",
                "user2",
                "user2__profile",
            )
            .annotate(
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
            .order_by("-updated_at")
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