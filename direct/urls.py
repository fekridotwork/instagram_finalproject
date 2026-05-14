from django.urls import path

from .views import ConversationListCreateAPIView


urlpatterns = [
    path(
        "conversations/",
        ConversationListCreateAPIView.as_view(),
        name="conversation-list-create",
    ),
]