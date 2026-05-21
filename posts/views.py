from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from interactions.models import Like, SavePost, Block
from interactions.schemas import (
    like_post_schema,
    save_post_schema,
    unlike_post_schema,
    unsave_post_schema,
)
from interactions.serializers import FollowUserSerializer
from interactions.services import exclude_blocked_content
from posts.services.annotations import annotate_post_interactions
from posts.services.search import (VALID_SEARCH_TYPES, normalize_search_term,
                                   search_posts, search_users)
from posts.services.visibility import can_view_post, can_view_profile

from .models import Post, Story
from .schemas import (
    post_create_schema,
    post_delete_schema,
    post_list_schema,
    post_retrieve_schema,
    post_update_schema,
    story_create_schema,
    story_delete_schema,
    story_list_schema,
)
from .serializers import (PostDetailSerializer, PostListSerializer,
                          PostSerializer, StorySerializer)
from .services.hashtags import sync_post_hashtags


@extend_schema_view(
    list=post_list_schema,
    create=post_create_schema,
    retrieve=post_retrieve_schema,
    update=post_update_schema,
    partial_update=post_update_schema,
    destroy=post_delete_schema,
)
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        queryset = exclude_blocked_content(
            Post.objects
            .filter(is_deleted=False)
            .select_related("user", "user__profile")
            .annotate(
                likes_count=Count("received_likes", distinct=True)
            ),
            self.request.user,
        )

        if self.action == "list":
            following_ids = self.request.user.following_relations.values(
                "following_id"
            )

            queryset = queryset.filter(
                Q(user=self.request.user)
                | Q(
                    user__profile__is_private=False,
                    visibility="public",
                )
                | Q(
                    user__in=following_ids,
                    visibility__in=["followers", "public"]
                )
            )
        queryset = annotate_post_interactions(
            queryset,
            self.request.user,
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
        post = serializer.save(user=self.request.user)
        sync_post_hashtags(post)

    def perform_update(self, serializer):
        has_changes = any(
            getattr(serializer.instance, field) != value
            for field, value in serializer.validated_data.items()
        )

        if has_changes:
            post = serializer.save(is_edited=True)
        else:
            post = serializer.save()

        sync_post_hashtags(post)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
    

    @like_post_schema
    @unlike_post_schema
    @action(detail=True, methods=["post", "delete"], url_path="like")
    def like(self, request, post_id=None):
        post = self.get_object()

        if not can_view_post(request.user, post):
            self.permission_denied(
                request,
                message="You do not have permission to like this post.",
            )

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
    

    @save_post_schema
    @unsave_post_schema
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

        if not can_view_profile(self.request.user, user):
            self.permission_denied(
                self.request,
                message="You do not have permission to view this profile.",
            )

        queryset = exclude_blocked_content(
            Post.objects
            .filter(
                user=user,
                is_deleted=False,
            )
            .select_related("user", "user__profile")
            .annotate(
                likes_count=Count("received_likes", distinct=True)
            )
            .order_by("-created_at"),
            self.request.user,
        )

        if user != self.request.user:
            queryset = queryset.filter(
                Q(visibility="public") |
                Q(visibility="followers")
            )
        
        queryset = annotate_post_interactions(
            queryset,
            self.request.user,
        )

        return queryset
    

@story_create_schema    
class StoryCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@story_list_schema
class StoryFeedAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def get_queryset(self):
        following_ids = self.request.user.following_relations.values(
            "following_id"
        )

        return exclude_blocked_content(
            Story.objects
            .filter(
                Q(user=self.request.user)
                | Q(
                    user__profile__is_private=False,
                    visibility="public",
                )
                | Q(
                    user__in=following_ids,
                    visibility__in=["public", "followers"],
                ),
                is_deleted=False,
                expires_at__gt=timezone.now(),
                user__is_active=True,
            )
            .select_related("user", "user__profile")
            .order_by("-created_at"),
            self.request.user,
        )
    
class GlobalSearchAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search", "")
        search_type = request.query_params.get("type", "all").lower()

        if search_type not in VALID_SEARCH_TYPES:
            return Response(
                {
                    "type": "Invalid search type. Choose from: all, users, posts."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not search.strip():
            return Response(
                {
                    "users": [],
                    "posts": [],
                },
                status=status.HTTP_200_OK,
            )

        normalized_search = normalize_search_term(search)

        return Response(
            {
                "users": search_users(
                    normalized_search,
                    request.user,
                    search_type,
                ),
                "posts": search_posts(
                    normalized_search,
                    request.user,
                    search_type,
                ),
            },
            status=status.HTTP_200_OK,
        )
class ExploreAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostListSerializer

    def get_queryset(self):
        queryset = exclude_blocked_content(
            Post.objects
            .filter(
                is_deleted=False,
                visibility="public",
                user__is_active=True,
                user__profile__is_private=False,
            )
            .select_related("user", "user__profile")
            .annotate(
                likes_count=Count("received_likes", distinct=True)
            )
            .order_by("-likes_count", "-created_at"),
            self.request.user,
        )

        queryset = annotate_post_interactions(
            queryset,
            self.request.user,
        )

        return queryset
