from django.urls import path

from .views import (
    UserFollowAPIView,
    MyFollowersListAPIView,
    MyFollowingListAPIView,
)

urlpatterns = [
    path(
        "users/<int:user_id>/follow/",
        UserFollowAPIView.as_view(),
        name="user-follow",
    ),
    path(
        "me/followers/",
        MyFollowersListAPIView.as_view(),
        name="my-followers",
    ),
    path(
        "me/following/",
        MyFollowingListAPIView.as_view(),
        name="my-following",
    ),
]