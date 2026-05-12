from django.urls import path

from .views import StoryCreateAPIView, StoryFeedAPIView

urlpatterns = [
    path(
        "",
        StoryCreateAPIView.as_view(),
        name="story-create",
    ),
    path(
        "feed/",
        StoryFeedAPIView.as_view(),
        name="story-feed",
    ),
]