from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets

from accounts.models import User

from .models import Post
from .serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
)

from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model

from django.db.models import Count, Q
from posts.permissions import can_view_post

from interactions.models import Like, SavePost

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        queryset = (
            Post.objects
            .filter(is_deleted=False)
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
        )

        if self.action == "list":
            queryset = queryset.filter(
                Q(user=self.request.user)
                | Q(user__profile__is_private=False, visibility="public")
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        return PostSerializer

    def get_object(self):
        post = super().get_object()

        if self.action == "retrieve":
            if not can_view_post(self.request.user, post):
                self.permission_denied(
                    self.request,
                    message="You do not have permission to view this post.",
                )

        elif self.action in ["update", "partial_update", "destroy"]:
            if post.user != self.request.user:
                self.permission_denied(
                    self.request,
                    message="You do not have permission to edit or delete this post.",
                )

        return post

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_edited=True)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
    
    @action(detail=True, methods=["post", "delete"], url_path="like")
    def like(self, request, post_id=None):
        post = self.get_object()

        if request.method == "POST":
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
    @action(detail=True, methods=["post", "delete"], url_path="save")
    def save(self, request, post_id=None):
        post = self.get_object()

        if not can_view_post(request.user, post):
            self.permission_denied(
                request,
                message="You do not have permission to save this post.",
            )

        if request.method == "POST":
            saved_post, created = SavePost.objects.get_or_create(
                user=request.user,
                post=post,
            )

            if not created:
                return Response(
                    {"message": "You have already saved this post."},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "Post saved successfully."},
                status=status.HTTP_201_CREATED,
            )

        saved_post = SavePost.objects.filter(
            user=request.user,
            post=post,
        ).first()

        if not saved_post:
            return Response(
                {"message": "You have not saved this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved_post.delete()

        return Response(
            {"message": "Post unsaved successfully."},
            status=status.HTTP_200_OK,
        )


class UserPostsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostListSerializer

    def get_user(self):
        return get_object_or_404(
            User,
            username=self.kwargs["username"],
            is_active=True,
        )
    def get_queryset(self):
        user = self.get_user()

        if user.profile.is_private and user != self.request.user:
            self.permission_denied(
                self.request,
                message="This account is private."
            )

        posts = (
            Post.objects
            .filter(user=user, is_deleted=False)
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
        )

        if user != self.request.user:
            posts = posts.filter(visibility="public")

        return posts

