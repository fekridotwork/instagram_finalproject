from django.db.models import Count, Exists, OuterRef, Q

from accounts.models import User
from interactions.serializers import FollowUserSerializer
from posts.models import Post
from posts.serializers import PostListSerializer
from posts.services.annotations import annotate_post_interactions

VALID_SEARCH_TYPES = {"all", "users", "posts"}
DEFAULT_SEARCH_LIMIT = 10


def normalize_search_term(search):
    return search.strip().lower().lstrip("#")


def search_users(search, user, search_type):
    if search_type not in {"all", "users"}:
        return []

    users = (
        User.objects
        .filter(
            username__icontains=search,
            is_active=True,
        )
        .exclude(id=user.id)
        .select_related("profile")
        .annotate(
            is_following=Exists(
                user.following_relations.filter(
                    following=OuterRef("pk"),
                )
            )
        )[:DEFAULT_SEARCH_LIMIT]
    )

    return FollowUserSerializer(users, many=True).data


def search_posts(search, user, search_type):
    if search_type not in {"all", "posts"}:
        return []

    following_ids = user.following_relations.values("following_id")

    posts = (
        Post.objects
        .filter(
            Q(user=user)
            | Q(
                user__profile__is_private=False,
                visibility="public",
            )
            | Q(
                user__in=following_ids,
                visibility__in=["public", "followers"],
            ),
            hashtags__name=search,
            is_deleted=False,
            user__is_active=True,
        )
        .select_related("user", "user__profile")
        .annotate(
            likes_count=Count("received_likes", distinct=True)
        )
        .order_by("-created_at")[:DEFAULT_SEARCH_LIMIT]
    )

    posts = annotate_post_interactions(posts, user)

    return PostListSerializer(posts, many=True).data