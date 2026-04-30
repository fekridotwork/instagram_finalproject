from django.urls import path

from .views import PostListCreateAPIView, PostDetailAPIView

urlpatterns = [
    path('', PostListCreateAPIView.as_view(), name="post-list-create"),
    path('<int:post_id>/', PostDetailAPIView.as_view(), name="post-detail"),
]