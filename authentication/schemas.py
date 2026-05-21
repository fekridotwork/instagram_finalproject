from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)

from config.swagger import detail_response

from rest_framework import serializers

from .serializers import (
    LogoutSerializer,
    MeSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
)

request_otp_schema = extend_schema(
    tags=["Authentication"],
    summary="Request OTP",
    description=(
        "Request an OTP code for login or registration using an email address "
        "or phone number. For login, the identifier must belong to an existing user. "
        "For registration, the identifier must not already be registered."
    ),
    request=RequestOTPSerializer,
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="RequestOTPResponse",
                fields={
                    "message": serializers.CharField(),
                    "code": serializers.CharField(required=False),
                },
            ),
            description=(
                "OTP sent successfully. In development mode, the OTP code may be "
                "included in the response for testing."
            ),
            examples=[
                OpenApiExample(
                    "OTP Sent",
                    value={
                        "message": "OTP sent successfully",
                        "code": "12345",
                    },
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=inline_serializer(
                name="RequestOTPBadRequestResponse",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
            description=(
                "Invalid request body, invalid purpose, invalid identifier, "
                "or registration attempted with an already registered identifier."
            ),
            examples=[
                OpenApiExample(
                    "User Already Exists",
                    value={
                        "detail": "User with this identifier already exists.",
                    },
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=inline_serializer(
                name="RequestOTPNotFoundResponse",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
            description="Login attempted with an identifier that does not belong to any user.",
            examples=[
                OpenApiExample(
                    "User Not Found",
                    value={
                        "detail": "User with this identifier does not exist.",
                    },
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=inline_serializer(
                name="RequestOTPRateLimitResponse",
                fields={
                    "detail": serializers.CharField(),
                    "retry_after": serializers.IntegerField(required=False),
                },
            ),
            description="OTP request is blocked by cooldown or rate limiting.",
            examples=[
                OpenApiExample(
                    "Cooldown Active",
                    value={
                        "detail": "Try again in 90 seconds.",
                        "retry_after": 90,
                    },
                    response_only=True,
                ),
            ],
        ),
    },
)


verify_otp_schema = extend_schema(
    tags=["Authentication"],
    summary="Verify OTP",
    description=(
        "Verify the OTP code sent to the user's email or phone number. "
        "If the code is valid, this endpoint returns JWT access and refresh tokens."
    ),
    request=VerifyOTPSerializer,
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="VerifyOTPResponse",
                fields={
                    "message": serializers.CharField(),
                    "is_new_user": serializers.BooleanField(),
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            ),
            description="OTP verified successfully. JWT tokens are returned.",
            examples=[
                OpenApiExample(
                    "Successful OTP Verification",
                    value={
                        "message": "OTP verified successfully",
                        "is_new_user": False,
                        "access": "eyJhbGciOi...",
                        "refresh": "eyJhbGciOi...",
                    },
                    response_only=True,
                ),
            ],
        ),
        400: detail_response(
            name="InvalidOTPResponse",
            description="Invalid OTP code, expired OTP, or invalid request body.",
            example_name="Invalid OTP",
            example_detail="Invalid OTP.",
        ),

        429: detail_response(
            name="TooManyOTPAttemptsResponse",
            description="Too many OTP verification attempts.",
            example_name="Too Many Attempts",
            example_detail="Too many attempts. Try again later.",
        ),
    },
)


logout_schema = extend_schema(
    tags=["Authentication"],
    summary="Logout User",
    description=(
        "Log out the authenticated user by blacklisting the provided refresh token. "
        "This endpoint requires a valid JWT access token in the Authorization header."
    ),
    request=LogoutSerializer,
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="LogoutResponse",
                fields={
                    "message": serializers.CharField(),
                },
            ),
            description="User logged out successfully.",
            examples=[
                OpenApiExample(
                    "Successful Logout",
                    value={
                        "message": "Logged out successfully",
                    },
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=inline_serializer(
                name="LogoutBadRequestResponse",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
            description="Invalid or malformed refresh token.",
            examples=[
                OpenApiExample(
                    "Invalid Refresh Token",
                    value={
                        "detail": "Invalid refresh token.",
                    },
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=inline_serializer(
                name="UnauthorizedResponse",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
            description="Authentication credentials were not provided or access token is invalid.",
            examples=[
                OpenApiExample(
                    "Unauthorized",
                    value={
                        "detail": "Authentication credentials were not provided.",
                    },
                    response_only=True,
                ),
            ],
        ),
    },
)

me_schema = extend_schema(
    tags=["Authentication"],
    summary="Get Current User Profile",
    description=(
        "Retrieve the authenticated user's basic profile information. "
        "A valid JWT access token must be provided in the Authorization header."
    ),
    responses={
        200: OpenApiResponse(
            response=MeSerializer,
            description="Authenticated user profile retrieved successfully.",
        ),
        401: OpenApiResponse(
            response=inline_serializer(
                name="MeUnauthorizedResponse",
                fields={
                    "detail": serializers.CharField(),
                },
            ),
            description="Authentication credentials were not provided or access token is invalid.",
            examples=[
                OpenApiExample(
                    "Unauthorized",
                    value={
                        "detail": "Authentication credentials were not provided.",
                    },
                    response_only=True,
                ),
            ],
        ),
    },
)