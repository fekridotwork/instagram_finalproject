from django.urls import path

from .views import PostListCreateAPIView, PostDetailAPIView
from interactions.views import PostLikeAPIView

urlpatterns = [
    path('', PostListCreateAPIView.as_view(), name="post-list-create"),
    path('<int:post_id>/', PostDetailAPIView.as_view(), name="post-detail"),
    path('<int:post_id>/like/', PostLikeAPIView.as_view(), name="post-like"),
]