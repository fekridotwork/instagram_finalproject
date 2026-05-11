from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import PostViewSet
from interactions.views import (
    PostLikeAPIView,
    CommentListCreateAPIView,
    CommentDetailAPIView,
)

router = SimpleRouter()
router.register("", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:post_id>/like/", PostLikeAPIView.as_view(), name="post-like"),
    path("<int:post_id>/comments/", CommentListCreateAPIView.as_view(), name="post-comment"),
    path("comment/<int:comment_id>/", CommentDetailAPIView.as_view(), name="comment-detail"),
]