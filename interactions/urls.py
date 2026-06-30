from django.urls import path

from interactions.views import UserBlockAPIView

from .views import (
    MutualFollowersAPIView,
    MyBlockedUsersListAPIView,
    MyFollowersListAPIView,
    MyFollowingListAPIView,
    MyBlockedUsersListAPIView,
    MySavedPostsListAPIView,
    UserFollowAPIView,
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
    path(
        "me/saved-posts/",
        MySavedPostsListAPIView.as_view(),
        name="my-saved-posts",
    ),
    path(
        "users/<int:user_id>/mutual-followers/",
        MutualFollowersAPIView.as_view(),
        name="mutual-followers",
    ),
    path(
        "block/",
        UserBlockAPIView.as_view(),
        name="user-block",
    ),
    path(
        "me/blocked-users/",
        MyBlockedUsersListAPIView.as_view(),
        name="my-blocked-users",
    ),
    path(
        "me/blocked-users/",
        MyBlockedUsersListAPIView.as_view(),
        name="my-blocked-users",
    ),
]