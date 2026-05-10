from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status

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


class PostListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Post.objects
            .filter(is_deleted=False)
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
            .filter(
                Q(user=self.request.user) |
                Q(user__profile__is_private=False, visibility="public")
            )
        )
    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        return (
            Post.objects
            .filter(is_deleted=False)
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PostDetailSerializer
        return PostSerializer
    
    def get_object(self):
        post = super().get_object()

        if self.request.method == "GET":
            if not can_view_post(self.request.user, post):
                self.permission_denied(
                    self.request,
                    message="You do not have permission to view this post."
                )
        elif post.user != self.request.user:
                self.permission_denied(
                    self.request,
                    message="You do not have permission to edit or delete this post."
                )
        return post
    def perform_update(self, serializer):
        print("DEBUG instance:", serializer.instance)
        print("DEBUG instance user_id:", serializer.instance.user_id)
        print("DEBUG validated data:", serializer.validated_data)
        serializer.save(is_edited=True)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])


User = get_user_model()

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

