from django.urls import path

from .views import PostHashtagSearchAPIView, UserSearchAPIView

urlpatterns = [
    path(
        "posts/",
        PostHashtagSearchAPIView.as_view(),
        name="post-hashtag-search",
    ),
    path(
        "users/",
        UserSearchAPIView.as_view(),
        name="user_search",
    )
]