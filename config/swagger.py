from drf_spectacular.utils import OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers


def detail_response(
    name,
    description,
    example_name,
    example_detail,
):
    return OpenApiResponse(
        response=inline_serializer(
            name=name,
            fields={
                "detail": serializers.CharField(),
            },
        ),
        description=description,
        examples=[
            OpenApiExample(
                example_name,
                value={
                    "detail": example_detail,
                },
                response_only=True,
            ),
        ],
    )


def unauthorized_response():
    return detail_response(
        name="UnauthorizedResponse",
        description="Authentication credentials were not provided or the access token is invalid.",
        example_name="Unauthorized",
        example_detail="Authentication credentials were not provided.",
    )


def not_found_response(
    name="NotFoundResponse",
    description="Requested resource was not found.",
    example_name="Not Found",
    example_detail="Not found.",
):
    return detail_response(
        name=name,
        description=description,
        example_name=example_name,
        example_detail=example_detail,
    )


def message_response(
    name,
    description,
    example_name,
    example_message,
):
    return OpenApiResponse(
        response=inline_serializer(
            name=name,
            fields={
                "message": serializers.CharField(),
            },
        ),
        description=description,
        examples=[
            OpenApiExample(
                example_name,
                value={
                    "message": example_message,
                },
                response_only=True,
            ),
        ],
    )