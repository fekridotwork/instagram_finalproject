from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from config.swagger import detail_response, not_found_response, unauthorized_response
from .serializers import (
    ConversationSerializer,
    DirectMessageSerializer,
    InboxConversationSerializer,
    StartConversationSerializer,
)

conversation_list_schema = extend_schema(
    tags=["Direct Messages"],
    summary="List Conversations",
    description=(
        "Return the authenticated user's inbox conversations. "
        "Each conversation includes the other participant and the latest message preview."
    ),
    responses={
        200: InboxConversationSerializer(many=True),
        401: unauthorized_response(),
    },
)


conversation_create_schema = extend_schema(
    tags=["Direct Messages"],
    summary="Start Conversation",
    description=(
        "Start a direct conversation with another active user. "
        "If a conversation already exists between the two users, the existing conversation is returned."
    ),
    request=StartConversationSerializer,
    responses={
        201: OpenApiResponse(
            response=ConversationSerializer,
            description="Conversation created successfully.",
        ),
        200: OpenApiResponse(
            response=ConversationSerializer,
            description="Existing conversation returned.",
        ),
        400: detail_response(
            name="ConversationCreateBadRequestResponse",
            description="Invalid request body or user attempted to start a conversation with themselves.",
            example_name="Invalid Conversation Request",
            example_detail="You cannot start a conversation with yourself.",
        ),
        401: unauthorized_response(),
        404: not_found_response(
            name="ConversationTargetUserNotFoundResponse",
            description="Target user was not found or is inactive.",
            example_detail="Not found.",
        ),
    },
)


conversation_messages_list_schema = extend_schema(
    tags=["Direct Messages"],
    summary="List Conversation Messages",
    description=(
        "Return all messages inside a conversation where the authenticated user "
        "is a participant."
    ),
    parameters=[
        OpenApiParameter(
            name="conversation_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the target conversation.",
            required=True,
        ),
    ],
    responses={
        200: DirectMessageSerializer(many=True),
        401: unauthorized_response(),
        403: detail_response(
            name="ConversationMessagesForbiddenResponse",
            description="The authenticated user is not a participant in this conversation.",
            example_name="Not Participant",
            example_detail="You do not have permission to access this conversation.",
        ),
        404: not_found_response(
            name="ConversationNotFoundResponse",
            description="Conversation not found.",
            example_detail="Not found.",
        ),
    },
)


conversation_message_create_schema = extend_schema(
    tags=["Direct Messages"],
    summary="Send Message",
    description=(
        "Send a new direct message inside a conversation where the authenticated "
        "user is a participant."
    ),
    parameters=[
        OpenApiParameter(
            name="conversation_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="ID of the target conversation.",
            required=True,
        ),
    ],
    request=DirectMessageSerializer,
    responses={
        201: OpenApiResponse(
            response=DirectMessageSerializer,
            description="Message sent successfully.",
        ),
        400: detail_response(
            name="SendMessageBadRequestResponse",
            description="Invalid message data.",
            example_name="Invalid Message",
            example_detail="Message text cannot be empty.",
        ),
        401: unauthorized_response(),
        403: detail_response(
            name="SendMessageForbiddenResponse",
            description="The authenticated user is not a participant in this conversation.",
            example_name="Not Participant",
            example_detail="You do not have permission to access this conversation.",
        ),
        404: not_found_response(
            name="SendMessageConversationNotFoundResponse",
            description="Conversation not found.",
            example_detail="Not found.",
        ),
    },
)