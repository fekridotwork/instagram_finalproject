from django.db.models import Exists, OuterRef, Value, BooleanField

from interactions.models import Follow


def annotate_follow_status(queryset, viewer):
    if not viewer or not viewer.is_authenticated:
        return queryset.annotate(
            is_following=Value(False, output_field=BooleanField())
        )

    return queryset.annotate(
        is_following=Exists(
            Follow.objects.filter(
                follower=viewer,
                following=OuterRef("pk"),
            )
        )
    )