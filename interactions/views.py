from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Post
from .models import Like


class PostLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_deleted=False)

        if post.user.profile.is_private and post.user != request.user:
            return Response(
                {"error": "You do not have permission to like this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if post.visibility == "followers" and post.user != request.user:
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