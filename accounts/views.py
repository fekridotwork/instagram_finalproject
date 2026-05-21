from drf_spectacular.utils import extend_schema_view
from django.db.models import Count, Exists, OuterRef, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.models import Profile
from accounts.serializers import PublicProfileSerializer
from posts.models import Post
from posts.services.visibility import can_view_profile

from .schemas import (
    my_profile_retrieve_schema,
    my_profile_update_schema,
    public_profile_retrieve_schema,
)
from .serializers import ProfileSerializer


@extend_schema_view(
    get=my_profile_retrieve_schema,
    put=my_profile_update_schema,
    patch=my_profile_update_schema,
)
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile
    

@extend_schema_view(
    get=public_profile_retrieve_schema,
)
class PublicProfileAPIView(generics.RetrieveAPIView):
    serializer_class = PublicProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "user__username"
    lookup_url_kwarg = "username"

    def get_object(self):
        profile = super().get_object()

        if not can_view_profile(self.request.user, profile.user):
            self.permission_denied(
                self.request,
                message="You do not have permission to view this profile.",
            )

        return profile

    def get_queryset(self):
        return (
            Profile.objects
            .filter(user__is_active=True)
            .select_related("user")
            .annotate(
                followers_count=Count("user__follower_relations", distinct=True),
                following_count=Count("user__following_relations", distinct=True),
                posts_count=Count(
                    "user__posts",
                    filter=Q(user__posts__is_deleted=False),
                    distinct=True,
                ),
                is_following=Exists(
                    self.request.user.following_relations.filter(
                        following=OuterRef("user_id"),
                    )
                ),
            )
        )