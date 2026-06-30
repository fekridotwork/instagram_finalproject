from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from config.swagger import detail_response, not_found_response, unauthorized_response
from posts.serializers import PostListSerializer

from .serializers import ProfileSerializer, PublicProfileSerializer, ProfileUpdateSerializer


my_profile_retrieve_schema = extend_schema(
    tags=["Profiles"],
    summary="Get My Profile",
    description=(
        "Return the authenticated user's own profile information, including "
        "username, full name, display name, bio, profile image, and privacy status."
    ),
    responses={
        200: OpenApiResponse(
            response=ProfileSerializer,
            description="Authenticated user's profile retrieved successfully.",
        ),
        401: unauthorized_response(),
    },
)


my_profile_update_schema = extend_schema(
    tags=["Profiles"],
    summary="Update My Profile",
    description=(
        "Update the authenticated user's own profile. "
        "This endpoint supports partial updates. The username is updated through "
        "the nested user field exposed by the serializer."
    ),
    request={
        "multipart/form-data": ProfileUpdateSerializer,
    },
    responses={
        200: OpenApiResponse(
            response=ProfileSerializer,
            description="Profile updated successfully.",
        ),
        400: detail_response(
            name="ProfileUpdateBadRequestResponse",
            description="Invalid profile data.",
            example_name="Invalid Profile Data",
            example_detail="Display name must be at least 3 characters.",
        ),
        401: unauthorized_response(),
    },
)


public_profile_retrieve_schema = extend_schema(
    tags=["Profiles"],
    summary="Get Public Profile",
    description=(
        "Return another user's public profile by username. "
        "The response includes profile information, follower/following counts, "
        "post count, and whether the authenticated user follows this profile. "
        "Profile visibility and block rules are respected."
    ),
    parameters=[
        OpenApiParameter(
            name="username",
            type=str,
            location=OpenApiParameter.PATH,
            description="Username of the target profile.",
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=PublicProfileSerializer,
            description="Public profile retrieved successfully.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="PublicProfileForbiddenResponse",
            description="The authenticated user is not allowed to view this profile.",
            example_name="Profile Not Visible",
            example_detail="You do not have permission to view this profile.",
        ),
        404: not_found_response(
            name="PublicProfileNotFoundResponse",
            description="Profile was not found or user is inactive.",
            example_detail="Not found.",
        ),
    },
)


user_posts_schema = extend_schema(
    tags=["Profiles"],
    summary="List User Posts",
    description=(
        "Return posts belonging to the target user identified by username. "
        "Only posts visible to the authenticated user are included, based on "
        "profile privacy, post visibility, follow relationships, deleted posts, "
        "inactive users, and block rules."
    ),
    parameters=[
        OpenApiParameter(
            name="username",
            type=str,
            location=OpenApiParameter.PATH,
            description="Username of the target user.",
            required=True,
        ),
    ],
    responses={
        200: PostListSerializer(many=True),
        401: unauthorized_response(),
        403: detail_response(
            name="UserPostsForbiddenResponse",
            description="The authenticated user is not allowed to view this user's posts.",
            example_name="Posts Not Visible",
            example_detail="You do not have permission to view these posts.",
        ),
        404: not_found_response(
            name="UserPostsNotFoundResponse",
            description="Target user was not found or inactive.",
            example_detail="Not found.",
        ),
    },
)