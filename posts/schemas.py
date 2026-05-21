from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from config.swagger import (
    detail_response,
    not_found_response,
    unauthorized_response,
)
from .serializers import (
    PostSerializer,
    PostDetailSerializer,
    PostListSerializer,
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
    request=PostSerializer,
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
    request=PostSerializer,
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