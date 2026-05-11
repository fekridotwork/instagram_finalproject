from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Post
from .models import Like, Comment
from .serializers import CommentSerializer

from posts.permissions import can_view_post


class CommentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_post(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"], is_deleted=False)

        if not can_view_post(self.request.user, post):
            self.permission_denied(
                self.request,
                message="You do not have permission to access comments on this post.",
            )
        return post
    def get_queryset(self):
        post = self.get_post()

        return (
            Comment.objects
            .filter(post=post, parent__isnull=True, is_deleted=False)
            .select_related("user")
        )
    
    def perform_create(self, serializer):
        post = self.get_post()
        parent = serializer.validated_data.get("parent")

        if parent and parent.post_id != post.id:
            raise serializer.ValidationError(
                {"parent": "Parent comment does not belong to this post."}
            )

        serializer.save(user=self.request.user, post=post)

        post.comments_count += 1
        post.save(update_fields=["comments_count"])

class CommentDetailAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.filter(is_deleted=False)
    lookup_url_kwarg = "comment_id"

    def get_object(self):
        comment = super().get_object()

        if (
            comment.user != self.request.user
            and comment.post.user != self.request.user
        ):
            self.permission_denied(
                self.request,
                message="You do not have permission to delete this comment.",
            )

        return comment

    def count_comment_tree(self, comment):
        count = 1

        for reply in comment.replies.filter(is_deleted=False):
            count += self.count_comment_tree(reply)

        return count

    def perform_destroy(self, instance):
        deleted_count = self.count_comment_tree(instance)

        instance.soft_delete_with_replies()

        post = instance.post
        post.comments_count = max(post.comments_count - deleted_count, 0)
        post.save(update_fields=["comments_count"])