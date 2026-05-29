from django.urls import include, path
from rest_framework.routers import SimpleRouter

from interactions.views import CommentDetailAPIView, CommentListCreateAPIView

from .views import PostViewSet, TrendingHashtagsAPIView

router = SimpleRouter()
router.register("", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:post_id>/comments/", CommentListCreateAPIView.as_view(), name="post-comment"),
    path("comment/<int:comment_id>/", CommentDetailAPIView.as_view(), name="comment-detail"),
    path(
        "hashtags/trending/",
        TrendingHashtagsAPIView.as_view(),
        name="trending-hashtags",
    ),
]