from django.urls import path

from .views import ConversationListCreateAPIView, ConversationMessagesAPIView

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
]