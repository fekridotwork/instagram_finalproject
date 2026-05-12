from django.urls import path

from .views import PostHashtagSearchAPIView

urlpatterns = [
    path(
        "posts/",
        PostHashtagSearchAPIView.as_view(),
        name="post-hashtag-search",
    ),
]