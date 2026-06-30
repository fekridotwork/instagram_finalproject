from django.urls import path

from .views import (
    ConversationListCreateAPIView,
    ConversationMessagesAPIView,
    DirectMessageDetailAPIView,
)
urlpatterns = [
    path(
        "conversations/",
        ConversationListCreateAPIView.as_view(),
        name="conversation-list-create",
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        ConversationMessagesAPIView.as_view(),
        name="conversation-messages",
    ),
    path(
        "messages/<int:message_id>/",
        DirectMessageDetailAPIView.as_view(),
        name="direct-message-detail",
    ),
]