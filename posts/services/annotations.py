from django.db.models import BooleanField, Exists, OuterRef, Value

from interactions.models import Like, SavePost


def annotate_post_interactions(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.annotate(
            is_liked=Value(False, output_field=BooleanField()),
            is_saved=Value(False, output_field=BooleanField()),
        )

    return queryset.annotate(
        is_liked=Exists(
            Like.objects.filter(
                user=user,
                post=OuterRef("pk"),
            )
        ),
        is_saved=Exists(
            SavePost.objects.filter(
                user=user,
                post=OuterRef("pk"),
            )
        ),
    )