from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Post
from .models import Like, Comment
from .serializers import CommentSerializer

from posts.permissions import can_view_post


class PostLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)

        if not can_view_post(request.user, post):
            return Response(
                {"error": "You do not have permission to like this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,
        )

        if not created:
            return Response(
                {"message": "You have already liked this post."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Post liked successfully."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)

        if not can_view_post(request.user, post):
            return Response(
                {"error": "You do not have permission to unlike this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        like = Like.objects.filter(
            user=request.user,
            post=post,
        ).first()

        if not like:
            return Response(
                {"message": "You have not liked this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        like.delete()

        return Response(
            {"message": "Post unliked successfully."},
            status=status.HTTP_200_OK,
        )

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
                message="You do not have permission to delete this comment."
            )
        return comment
    
    def perform_destroy(self, instance):
        deleted_count = 1

        if instance.parent is None:
            replies_count = Comment.objects.filter(
                parent=instance,
                is_deleted=False,
            ).update(is_deleted=True)
            
            deleted_count += replies_count

        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

        post = instance.post
        post.comments_count = max(post.comments_count - deleted_count, 0)
        post.save(update_fields=["comments_count"])

    