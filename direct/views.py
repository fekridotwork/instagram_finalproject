from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q

from accounts.models import User
from .models import DirectConversation
from .serializers import (
    StartConversationSerializer,
    ConversationSerializer,
    InboxConversationSerializer,
)

class ConversationListCreateAPIView(generics.GenericAPIView):
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