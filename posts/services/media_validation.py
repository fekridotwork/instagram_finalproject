from rest_framework import serializers


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_VIDEO_SIZE = 20 * 1024 * 1024

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
}


def validate_media_file(media, media_type):
    if not media:
        return

    content_type = getattr(media, "content_type", None)
    size = getattr(media, "size", 0)

    if media_type == "image":
        if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise serializers.ValidationError(
                {
                    "media": "Upload a valid image file."
                }
            )

        if size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError(
                {
                    "media": "Image file size must be 5MB or less."
                }
            )

    elif media_type == "video":
        if content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
            raise serializers.ValidationError(
                {
                    "media": "Upload a valid video file."
                }
            )

        if size > MAX_VIDEO_SIZE:
            raise serializers.ValidationError(
                {
                    "media": "Video file size must be 20MB or less."
                }
            )
        else:
            raise serializers.ValidationError(
                {
                    "media_type": "Invalid media type."
                }
            )