from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers

from config.swagger import (
    detail_response,
    message_response,
    not_found_response,
    unauthorized_response,
)
from posts.serializers import PostListSerializer
from .serializers import BlockUserSerializer, CommentSerializer, FollowUserSerializer

follow_schema = extend_schema(
    tags=["Interactions - Follow"],
    summary="Follow User",
    description=(
        "Follow an active user by user ID. "
        "The authenticated user cannot follow themselves and cannot follow users "
        "when either side has blocked the other."
    ),
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the user to follow.",
            required=True,
        ),
    ],
    request=None,
    responses={
        201: message_response(
            name="FollowUserCreatedResponse",
            description="User followed successfully.",
            example_name="Followed",
            example_message="User followed successfully.",
        ),
        200: message_response(
            name="AlreadyFollowingResponse",
            description="The authenticated user already follows this user.",
            example_name="Already Following",
            example_message="You already follow this user.",
        ),
        400: message_response(
            name="FollowBadRequestResponse",
            description="The authenticated user attempted to follow themselves.",
            example_name="Cannot Follow Self",
            example_message="You cannot follow yourself.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="FollowForbiddenResponse",
            description="The authenticated user is not allowed to follow this user.",
            example_name="Follow Forbidden",
            example_detail="You cannot follow this user.",
        ),
        404: not_found_response(
            name="FollowUserNotFoundResponse",
            description="Target user was not found or is inactive.",
            example_detail="Not found.",
        ),
    },
)



unfollow_schema = extend_schema(
    tags=["Interactions - Follow"],
    summary="Unfollow User",
    description="Unfollow an active user by user ID.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the user to unfollow.",
            required=True,
        ),
    ],
    request=None,
    responses={
        200: message_response(
            name="UnfollowUserResponse",
            description="User unfollowed successfully.",
            example_name="Unfollowed",
            example_message="User unfollowed successfully.",
        ),
        400: message_response(
            name="NotFollowingResponse",
            description="The authenticated user does not follow this user.",
            example_name="Not Following",
            example_message="You do not follow this user.",
        ),
        401: unauthorized_response(),
        404: not_found_response(
            name="UnfollowUserNotFoundResponse",
            description="Target user was not found or is inactive.",
            example_detail="Not found.",
        ),
    },
)


block_schema = extend_schema(
    tags=["Interactions - Block"],
    summary="Block User",
    description=(
        "Block another user. After blocking, both follow relationships between "
        "the authenticated user and the target user are removed. Blocked users "
        "should not appear in search or be able to interact normally."
    ),
    request=BlockUserSerializer,
    responses={
        200: message_response(
            name="BlockUserResponse",
            description="User blocked successfully.",
            example_name="Blocked",
            example_message="User blocked successfully.",
        ),
        400: detail_response(
            name="BlockBadRequestResponse",
            description="Invalid request body or user attempted to block themselves.",
            example_name="Cannot Block Self",
            example_detail="You cannot block yourself.",
        ),
        401: unauthorized_response(),
        404: not_found_response(
            name="BlockUserNotFoundResponse",
            description="Target user was not found or is inactive.",
            example_detail="Not found.",
        ),
    },
)

unblock_schema = extend_schema(
    tags=["Interactions - Block"],
    summary="Unblock User",
    description=(
        "Unblock a previously blocked user. This does not restore any previous "
        "follow relationship automatically."
    ),
    request=BlockUserSerializer,
    responses={
        200: message_response(
            name="UnblockUserResponse",
            description="User unblocked successfully.",
            example_name="Unblocked",
            example_message="User unblocked successfully.",
        ),
        400: detail_response(
            name="UnblockBadRequestResponse",
            description="Invalid request body or the user was not blocked.",
            example_name="Not Blocked",
            example_detail="You have not blocked this user.",
        ),
        401: unauthorized_response(),
        404: not_found_response(
            name="UnblockUserNotFoundResponse",
            description="Target user was not found or is inactive.",
            example_detail="Not found.",
        ),
    },
)


my_followers_schema = extend_schema(
    tags=["Interactions - Follow"],
    summary="List My Followers",
    description=(
        "Return the list of active users who follow the authenticated user. "
        "Each item includes basic user/profile information and whether the "
        "authenticated user follows them back."
    ),
    responses={
        200: FollowUserSerializer(many=True),
        401: unauthorized_response(),
    },
)


my_following_schema = extend_schema(
    tags=["Interactions - Follow"],
    summary="List My Following",
    description=(
        "Return the list of active users that the authenticated user follows. "
        "Each item includes basic user/profile information and follow status."
    ),
    responses={
        200: FollowUserSerializer(many=True),
        401: unauthorized_response(),
    },
)


mutual_followers_schema = extend_schema(
    tags=["Interactions - Follow"],
    summary="List Mutual Following Users",
    description=(
        "Return users that are followed by both the authenticated user and the "
        "target user. The target user is identified by the user_id path parameter."
    ),
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the target user used to calculate mutual following users.",
            required=True,
        ),
    ],
    responses={
        200: FollowUserSerializer(many=True),
        401: unauthorized_response(),
        404: not_found_response(
            name="MutualFollowersUserNotFoundResponse",
            description="Target user was not found or is inactive.",
            example_detail="Not found.",
        ),
    },
)


my_saved_posts_schema = extend_schema(
    tags=["Interactions - Save"],
    summary="List My Saved Posts",
    description=(
        "Return posts saved by the authenticated user. Results respect post visibility, "
        "privacy rules, deleted posts, inactive users, and block relationships."
    ),
    responses={
        200: PostListSerializer(many=True),
        401: unauthorized_response(),
    },
)

like_post_schema = extend_schema(
    methods=["POST"],
    tags=["Interactions - Like"],
    summary="Like Post",
    description=(
        "Like a visible post by post ID. The authenticated user must be able "
        "to view the post based on post visibility, follow status, and block rules."
    ),
    request=None,
    responses={
        201: message_response(
            name="LikePostResponse",
            description="Post liked successfully.",
            example_name="Liked",
            example_message="Post liked successfully.",
        ),
        400: detail_response(
            name="AlreadyLikedPostResponse",
            description="The authenticated user has already liked this post.",
            example_name="Already Liked",
            example_detail="You have already liked this post.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="LikePostForbiddenResponse",
            description="The authenticated user cannot interact with this post.",
            example_name="Forbidden",
            example_detail="You do not have permission to interact with this post.",
        ),
        404: not_found_response(
            name="LikePostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


unlike_post_schema = extend_schema(
    methods=["DELETE"],
    tags=["Interactions - Like"],
    summary="Unlike Post",
    description="Remove the authenticated user's like from a visible post.",
    request=None,
    responses={
        200: message_response(
            name="UnlikePostResponse",
            description="Post unliked successfully.",
            example_name="Unliked",
            example_message="Post unliked successfully.",
        ),
        400: detail_response(
            name="PostNotLikedResponse",
            description="The authenticated user has not liked this post.",
            example_name="Not Liked",
            example_detail="You have not liked this post.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="UnlikePostForbiddenResponse",
            description="The authenticated user cannot interact with this post.",
            example_name="Forbidden",
            example_detail="You do not have permission to interact with this post.",
        ),
        404: not_found_response(
            name="UnlikePostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


save_post_schema = extend_schema(
    methods=["POST"],
    tags=["Interactions - Save"],
    summary="Save Post",
    description=(
        "Save a visible post to the authenticated user's saved posts. "
        "The authenticated user must be able to view the post."
    ),
    request=None,
    responses={
        201: message_response(
            name="SavePostResponse",
            description="Post saved successfully.",
            example_name="Saved",
            example_message="Post saved successfully.",
        ),
        400: detail_response(
            name="AlreadySavedPostResponse",
            description="The authenticated user has already saved this post.",
            example_name="Already Saved",
            example_detail="You have already saved this post.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="SavePostForbiddenResponse",
            description="The authenticated user cannot interact with this post.",
            example_name="Forbidden",
            example_detail="You do not have permission to interact with this post.",
        ),
        404: not_found_response(
            name="SavePostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


unsave_post_schema = extend_schema(
    methods=["DELETE"],
    tags=["Interactions - Save"],
    summary="Unsave Post",
    description="Remove a post from the authenticated user's saved posts.",
    request=None,
    responses={
        200: message_response(
            name="UnsavePostResponse",
            description="Post unsaved successfully.",
            example_name="Unsaved",
            example_message="Post unsaved successfully.",
        ),
        400: detail_response(
            name="PostNotSavedResponse",
            description="The authenticated user has not saved this post.",
            example_name="Not Saved",
            example_detail="You have not saved this post.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="UnsavePostForbiddenResponse",
            description="The authenticated user cannot interact with this post.",
            example_name="Forbidden",
            example_detail="You do not have permission to interact with this post.",
        ),
        404: not_found_response(
            name="UnsavePostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


comment_list_schema = extend_schema(
    tags=["Interactions - Comments"],
    summary="List Post Comments",
    description=(
        "Return top-level comments for a visible post. "
        "Replies are included inside each comment. "
        "The authenticated user must have permission to view the post."
    ),
    parameters=[
        OpenApiParameter(
            name="post_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the post whose comments should be listed.",
            required=True,
        ),
    ],
    responses={
        200: CommentSerializer(many=True),
        401: unauthorized_response(),
        403: detail_response(
            name="CommentListForbiddenResponse",
            description="The authenticated user cannot view comments on this post.",
            example_name="Cannot View Comments",
            example_detail="You do not have permission to access comments on this post.",
        ),
        404: not_found_response(
            name="CommentListPostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


comment_create_schema = extend_schema(
    tags=["Interactions - Comments"],
    summary="Create Comment",
    description=(
        "Create a comment on a visible post. "
        "To create a reply, pass the parent comment ID in the parent field. "
        "The parent comment must belong to the same post."
    ),
    parameters=[
        OpenApiParameter(
            name="post_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the post to comment on.",
            required=True,
        ),
    ],
    request=CommentSerializer,
    responses={
        201: OpenApiResponse(
            response=CommentSerializer,
            description="Comment created successfully.",
        ),
        400: detail_response(
            name="CommentCreateBadRequestResponse",
            description="Invalid comment data, empty text, text longer than 500 characters, or invalid parent comment.",
            example_name="Invalid Comment",
            example_detail="Comment cannot be empty.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="CommentCreateForbiddenResponse",
            description="The authenticated user cannot comment on this post.",
            example_name="Cannot Comment",
            example_detail="You do not have permission to access comments on this post.",
        ),
        404: not_found_response(
            name="CommentCreatePostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


comment_delete_schema = extend_schema(
    tags=["Interactions - Comments"],
    summary="Delete Comment",
    description=(
        "Soft delete a comment by comment ID. "
        "Only the comment owner or the owner of the post can delete the comment. "
        "If the comment has replies, the comment tree is soft-deleted and the post comment count is updated."
    ),
    parameters=[
        OpenApiParameter(
            name="comment_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the comment to delete.",
            required=True,
        ),
    ],
    responses={
        204: OpenApiResponse(description="Comment deleted successfully."),
        401: unauthorized_response(),
        403: detail_response(
            name="CommentDeleteForbiddenResponse",
            description="Only the comment owner or post owner can delete this comment.",
            example_name="Cannot Delete Comment",
            example_detail="You do not have permission to delete this comment.",
        ),
        404: not_found_response(
            name="CommentDeleteNotFoundResponse",
            description="Comment was not found or has already been deleted.",
            example_detail="Not found.",
        ),
    },
)