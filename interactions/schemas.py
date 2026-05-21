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
    tags=["Interactions"],
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
    tags=["Interactions"],
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
    tags=["Interactions"],
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
    tags=["Interactions"],
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
    tags=["Interactions"],
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
    tags=["Interactions"],
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
    tags=["Interactions"],
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
    tags=["Interactions"],
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