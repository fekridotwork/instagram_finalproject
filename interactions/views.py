from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
 
from accounts.models import User
from posts.models import Post
from posts.permissions import can_view_post
from posts.serializers import PostListSerializer

from .models import Comment, Follow, SavePost
from .serializers import CommentSerializer, FollowUserSerializer



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

class UserFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_target_user(self, user_id):
        return get_object_or_404(User, id=user_id, is_active=True)

    def post(self, request, user_id):
        target_user = self.get_target_user(user_id)

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

class MyFollowersListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        follow_relations = Follow.objects.filter(
            following=self.request.user,
        ).select_related("follower")

        return [relation.follower for relation in follow_relations]
    
class MyFollowingListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        follow_relations = Follow.objects.filter(
            follower=self.request.user,
        ).select_related("following")

        return [relation.following for relation in follow_relations]
class MySavedPostsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostListSerializer

    def get_queryset(self):
        return (
            Post.objects
            .filter(
                id__in=SavePost.objects.filter(
                    user=self.request.user
                ).values("post_id"),
                is_deleted=False,
            )
            .select_related("user")
            .annotate(likes_count=Count("received_likes"))
        )