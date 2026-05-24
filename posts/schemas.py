from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)

from rest_framework import serializers

from interactions.serializers import FollowUserSerializer

from config.swagger import (
    detail_response,
    not_found_response,
    unauthorized_response,
)
from .serializers import (
    PostSerializer,
    PostDetailSerializer,
    PostListSerializer,
    StorySerializer
)

class PostCreateRequestSerializer(serializers.Serializer):
    media = serializers.FileField()
    media_type = serializers.ChoiceField(choices=["image", "video", "text"])
    caption = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=["public", "followers"],
        required=False,
    )


class PostUpdateRequestSerializer(serializers.Serializer):
    media = serializers.FileField(required=False)
    media_type = serializers.ChoiceField(
        choices=["image", "video", "text"],
        required=False,
    )
    caption = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=["public", "followers"],
        required=False,
    )

class StoryCreateRequestSerializer(serializers.Serializer):
    media = serializers.FileField(required=False)
    media_type = serializers.ChoiceField(choices=["image", "video", "text"])
    text = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=["public", "followers"],
        required=False,
    )

post_list_schema = extend_schema(
    tags=["Posts"],
    summary="List Visible Posts",
    description=(
        "Return a list of posts visible to the authenticated user. "
        "The result respects public/followers-only visibility, deleted posts, "
        "inactive users, and block relationships."
    ),
    responses={
        200: PostListSerializer(many=True),
        401: unauthorized_response(),
    },
)


post_create_schema = extend_schema(
    tags=["Posts"],
    summary="Create Post",
    description=(
        "Create a new post with an image or video file, caption, and visibility. "
        "The request must be sent as multipart/form-data."
    ),
    request={"multipart/form-data": PostCreateRequestSerializer},
    responses={
        201: OpenApiResponse(
            response=PostDetailSerializer,
            description="Post created successfully.",
        ),
        400: detail_response(
            name="PostCreateBadRequestResponse",
            description="Invalid post data, invalid media file, or unsupported media type.",
            example_name="Invalid Post Data",
            example_detail="Invalid media file.",
        ),
        401: unauthorized_response(),
    },
)


post_retrieve_schema = extend_schema(
    tags=["Posts"],
    summary="Retrieve Post Detail",
    description=(
        "Retrieve details of a single post by ID. The authenticated user must have "
        "permission to view the post based on visibility, follow status, and block rules."
    ),
    responses={
        200: PostDetailSerializer,
        401: unauthorized_response(),
        403: detail_response(
            name="PostDetailForbiddenResponse",
            description="The authenticated user does not have permission to view this post.",
            example_name="Post Not Visible",
            example_detail="You do not have permission to view this post.",
        ),
        404: not_found_response(
            name="PostNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


post_update_schema = extend_schema(
    tags=["Posts"],
    summary="Update Post",
    description=(
        "Partially update a post owned by the authenticated user. "
        "Caption, visibility, and media can be updated. Media is not required for partial updates."
    ),
    request={"multipart/form_data": PostUpdateRequestSerializer},
    responses={
        200: PostDetailSerializer,
        400: detail_response(
            name="PostUpdateBadRequestResponse",
            description="Invalid update data or invalid media file.",
            example_name="Invalid Update Data",
            example_detail="Invalid media file.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="PostUpdateForbiddenResponse",
            description="Only the post owner can update this post.",
            example_name="Not Post Owner",
            example_detail="You do not have permission to edit this post.",
        ),
        404: not_found_response(
            name="PostUpdateNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


post_delete_schema = extend_schema(
    tags=["Posts"],
    summary="Delete Post",
    description=(
        "Soft delete a post owned by the authenticated user. "
        "The post is marked as deleted instead of being physically removed from the database."
    ),
    responses={
        204: OpenApiResponse(description="Post deleted successfully."),
        401: unauthorized_response(),
        403: detail_response(
            name="PostDeleteForbiddenResponse",
            description="Only the post owner can delete this post.",
            example_name="Not Post Owner",
            example_detail="You do not have permission to delete this post.",
        ),
        404: not_found_response(
            name="PostDeleteNotFoundResponse",
            description="Post was not found or has been deleted.",
            example_detail="Not found.",
        ),
    },
)


story_list_schema = extend_schema(
    tags=["Stories"],
    summary="List Story Feed",
    description=(
        "Return visible stories for the authenticated user. "
        "Only non-expired stories are included. Visibility, follow relationships, "
        "deleted stories, inactive users, and block rules are respected."
    ),
    responses={
        200: StorySerializer(many=True),
        401: unauthorized_response(),
    },
)


story_create_schema = extend_schema(
    tags=["Stories"],
    summary="Create Story",
    description=(
        "Create a new story with media, optional text, and visibility settings. "
        "The request must be sent as multipart/form-data."
    ),
    request={"multipart/form-data": StoryCreateRequestSerializer},
    responses={
        201: OpenApiResponse(
            response=StorySerializer,
            description="Story created successfully.",
        ),
        400: detail_response(
            name="StoryCreateBadRequestResponse",
            description="Invalid story data or unsupported media.",
            example_name="Invalid Story",
            example_detail="Invalid media file.",
        ),
        401: unauthorized_response(),
    },
)


story_delete_schema = extend_schema(
    tags=["Stories"],
    summary="Delete Story",
    description=(
        "Soft delete a story owned by the authenticated user."
    ),
    parameters=[
        OpenApiParameter(
            name="story_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the story to delete.",
            required=True,
        ),
    ],
    responses={
        204: OpenApiResponse(
            description="Story deleted successfully.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="StoryDeleteForbiddenResponse",
            description="Only the story owner can delete this story.",
            example_name="Cannot Delete Story",
            example_detail="You do not have permission to delete this story.",
        ),
        404: not_found_response(
            name="StoryNotFoundResponse",
            description="Story not found or already deleted.",
            example_detail="Not found.",
        ),
    },
)

global_search_schema = extend_schema(
    tags=["Discovery"],
    summary="Global Search",
    description=(
        "Search users by username and posts by hashtag. "
        "Use the type query parameter to limit results to users, posts, or all. "
        "Blocked users and content are excluded from the results."
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            type=str,
            location=OpenApiParameter.QUERY,
            description=(
                "Search keyword. For post search, hashtags can be passed with or without #."
            ),
            required=False,
        ),
        OpenApiParameter(
            name="type",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Search type. Valid values: all, users, posts.",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="GlobalSearchResponse",
                fields={
                    "users": FollowUserSerializer(many=True),
                    "posts": PostListSerializer(many=True),
                },
            ),
            description="Search results returned successfully.",
            examples=[
                OpenApiExample(
                    "Search Results",
                    value={
                        "users": [],
                        "posts": [],
                    },
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=inline_serializer(
                name="GlobalSearchBadRequestResponse",
                fields={
                    "type": serializers.CharField(),
                },
            ),
            description="Invalid search type.",
            examples=[
                OpenApiExample(
                    "Invalid Search Type",
                    value={
                        "type": "Invalid search type. Choose from: all, users, posts."
                    },
                    response_only=True,
                ),
            ],
        ),
        401: unauthorized_response(),
    },
)


explore_schema = extend_schema(
    tags=["Discovery"],
    summary="Explore Public Posts",
    description=(
        "Return public posts from active, non-private users. "
        "Deleted posts and blocked users/content are excluded. "
        "Posts are ordered by like count and creation date."
    ),
    responses={
        200: PostListSerializer(many=True),
        401: unauthorized_response(),
    },
)