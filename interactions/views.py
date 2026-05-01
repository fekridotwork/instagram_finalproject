from django.shortcuts import get_object_or_404
from rest_framework import status
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

class CommentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)

        if not can_view_post(request.user, post):
            return Response(
                {"error": "You do not have permission to view comments on this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comments = (
            Comment.objects
            .filter(post=post, parent__isnull=True, is_deleted=False)
            .select_related("user")
        )

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        post = get_object_or_404(
            Post,
            id=post_id,
            is_deleted=False
        )

        if not can_view_post(request.user, post):
            return Response(
                {"error": "You do not have permission to comment on this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = serializer.validated_data.get("parent")

        if parent and parent.post_id != post.id:
            return Response(
                {"error": "Parent comment does not belong to this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user, post=post)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(
            Comment.objects.select_related("user", "post", "post__user"),
            id=comment_id,
            is_deleted=False,
        )

        if comment.user != request.user and comment.post.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.soft_delete_with_replies()

        return Response(
            {"message": "Comment deleted successfully."},
            status=status.HTTP_200_OK,
        )