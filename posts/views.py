from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Post
from .serializers import PostSerializer

from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model

from django.db.models import Count, Q
from posts.permissions import can_view_post


class PostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        posts = (
            Post.objects
            .filter(is_deleted=False)
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
            .filter(
                Q(user=request.user) |
                Q(user__profile__is_private=False, visibility="public")
            )
        )

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # helper
    def get_object(self, post_id):
        return get_object_or_404(
            Post.objects
            .select_related("user")
            .annotate(likes_count=Count("received_likes")),
            id=post_id,
            is_deleted=False,
        )

    def get(self, request, post_id):
        post = self.get_object(post_id)

        if not can_view_post(request.user, post):
            return Response(
                {"error": "You do not have permission to view this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostSerializer(post)
        return Response(serializer.data)

    def patch(self, request, post_id):
        post = self.get_object(post_id)

        if post.user != request.user:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PostSerializer(
            post,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(is_edited=True)

        return Response(serializer.data)

    def delete(self, request, post_id):
        post = self.get_object(post_id)

        if post.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        post.is_deleted = True
        post.save(update_fields=["is_deleted"])

        return Response(
            {"message": "Post has been deleted successfully."},
            status=status.HTTP_200_OK,
        )

User = get_user_model()

class UserPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(
            User,
            username=username,
            is_active=True,
        )

        if user.profile.is_private and user != request.user:
            return Response(
                {"error": "This account is private."},
                status=status.HTTP_403_FORBIDDEN,
            )

        posts = (
            Post.objects
            .filter(user=user, is_deleted=False)
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
        )

        if user != request.user:
            posts = posts.filter(visibility="public")

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)