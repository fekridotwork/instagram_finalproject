from drf_spectacular.utils import OpenApiResponse, extend_schema


health_check_schema = extend_schema(
    tags=["System"],
    summary="Health Check",
    description="Check whether the API service is running.",
    responses={
        200: OpenApiResponse(
            description="Service is healthy.",
        ),
    },
)