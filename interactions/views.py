from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from drf_spectacular.utils import extend_schema_view
from interactions.serializers import BlockUserSerializer
from interactions.services import (
    block_user, unblock_user, 
    annotate_follow_status, 
    is_blocked_between
)
from interactions.services import exclude_blocked_content
from posts.models import Post
from posts.serializers import PostListSerializer
from posts.services.annotations import annotate_post_interactions
from posts.services.visibility import can_view_post

from .models import Comment, Follow, SavePost
from .schemas import (
    block_schema,
    comment_create_schema,
    comment_delete_schema,
    comment_list_schema,
    follow_schema,
    mutual_followers_schema,
    my_followers_schema,
    my_following_schema,
    my_saved_posts_schema,
    unfollow_schema,
    unblock_schema,
)
from .serializers import CommentSerializer, FollowUserSerializer


@extend_schema_view(
    get=comment_list_schema,
    post=comment_create_schema,
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

        if not can_view_post(self.request.user, post):
            self.permission_denied(
                self.request,
                message="You do not have permission to comment on this post.",
            )

        parent = serializer.validated_data.get("parent")

        if parent and parent.post != post:
            raise serializers.ValidationError(
                {"parent": "Parent comment does not belong to this post."}
            )

        serializer.save(
            user=self.request.user,
            post=post,
        )

        post.comments_count += 1
        post.save(update_fields=["comments_count"])


@extend_schema_view(
    delete=comment_delete_schema,
)
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


@extend_schema_view(
    post=follow_schema,
    delete=unfollow_schema,
)
class UserFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_target_user(self, user_id):
        return get_object_or_404(User, id=user_id, is_active=True)
    

    def post(self, request, user_id):
        target_user = self.get_target_user(user_id)

        if is_blocked_between(request.user, target_user):
            self.permission_denied(
                request,
                message="You cannot follow this user.",
            )

        if target_user == request.user:
            return Response(
                {"message": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user,
        )

        if not created:
            return Response(
                {"message": "You already follow this user."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "User followed successfully."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, user_id):
        target_user = self.get_target_user(user_id)

        follow = Follow.objects.filter(
            follower=request.user,
            following=target_user,
        ).first()

        if not follow:
            return Response(
                {"message": "You do not follow this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow.delete()

        return Response(
            {"message": "User unfollowed successfully."},
            status=status.HTTP_200_OK,
        )
    

@extend_schema_view(
    post=block_schema,
    delete=unblock_schema,
)    
class UserBlockAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BlockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user = get_object_or_404(
            User,
            id=serializer.validated_data["user_id"],
            is_active=True,
        )

        try:
            block_user(request.user, target_user)
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "User blocked successfully."},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        data = request.data.copy()
        if not data.get("user_id"):
            data["user_id"] = request.query_params.get("user_id")

        serializer = BlockUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        target_user = get_object_or_404(
            User,
            id=serializer.validated_data["user_id"],
            is_active=True,
        )

        try:
            unblock_user(request.user, target_user)
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "User unblocked successfully."},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(get=my_followers_schema)
class MyFollowersListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        queryset = (
            User.objects
            .filter(
                id__in=Follow.objects.filter(
                    following=self.request.user,
                ).values("follower_id"),
                is_active=True,
            )
            .select_related("profile")
        )

        queryset = annotate_follow_status(
            queryset,
            self.request.user,
        )

        return queryset
    

@extend_schema_view(get=my_following_schema)    
class MyFollowingListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        queryset = (
            User.objects
            .filter(
                id__in=Follow.objects.filter(
                    follower=self.request.user,
                ).values("following_id"),
                is_active=True,
            )
            .select_related("profile")
        )

        queryset = annotate_follow_status(
            queryset,
            self.request.user,
        )

        return queryset
    

@extend_schema_view(get=mutual_followers_schema)    
class MutualFollowersAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        target_user = get_object_or_404(
            User,
            id=self.kwargs["user_id"],
            is_active=True,
        )

        my_following_ids = Follow.objects.filter(
            follower=self.request.user,
        ).values_list("following_id", flat=True)

        target_following_ids = Follow.objects.filter(
            follower=target_user,
        ).values_list("following_id", flat=True)

        queryset = (
            User.objects
            .filter(id__in=my_following_ids)
            .filter(id__in=target_following_ids)
            .filter(is_active=True)
            .select_related("profile")
        )

        queryset = annotate_follow_status(
            queryset,
            self.request.user,
        )

        return queryset
    

@extend_schema_view(get=my_saved_posts_schema)    
class MySavedPostsListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_ids = self.request.user.following_relations.values(
            "following_id"
        )

        queryset = (
            Post.objects
            .filter(
                Q(user=self.request.user)
                | Q(user__profile__is_private=False, visibility="public")
                | Q(
                    user__in=following_ids,
                    visibility__in=["public", "followers"],
                ),
                id__in=SavePost.objects.filter(
                    user=self.request.user
                ).values("post_id"),
                is_deleted=False,
                user__is_active=True,
            )
            .select_related("user", "user__profile")
            .annotate(
                likes_count=Count("received_likes", distinct=True)
            )
            .order_by("-created_at")
        )

        queryset = exclude_blocked_content(
            queryset,
            self.request.user,
        )

        queryset = annotate_post_interactions(
            queryset,
            self.request.user,
        )

        return queryset

