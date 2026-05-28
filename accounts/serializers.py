from rest_framework import serializers

from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")

    class Meta:
        model = Profile
        fields = [
            "username",
            "full_name",
            "display_name",
            "bio",
            "profile_image",
            "is_private",
        ]
    def validate_display_name(self, value):
        value = value.strip()

        if value and len(value) < 3:
            raise serializers.ValidationError("Display name must be at least 3 characters")
        return value

    def validate_full_name(self, value):
        value = value.strip()

        if value and len(value) < 3:
            raise serializers.ValidationError("Full name is too short")
        return value

    def validate_bio(self, value):
        if value and len(value) > 300:
            raise serializers.ValidationError("Bio is too long")
        return value

    # override
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        # update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # update user fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return instance
    

class ProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", required=False)

    class Meta:
        model = Profile
        fields = [
            "username",
            "full_name",
            "display_name",
            "bio",
            "profile_image",
            "is_private",
        ]

    def validate_display_name(self, value):
        value = value.strip()

        if value and len(value) < 3:
            raise serializers.ValidationError("Display name must be at least 3 characters")
        return value

    def validate_full_name(self, value):
        value = value.strip()

        if value and len(value) < 3:
            raise serializers.ValidationError("Full name is too short")
        return value

    def validate_bio(self, value):
        if value and len(value) > 300:
            raise serializers.ValidationError("Bio is too long")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return instance


class PublicProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)
    is_blocked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "full_name",
            "display_name",
            "bio",
            "profile_image",
            "is_private",
            "is_active",
            "followers_count",
            "following_count",
            "posts_count",
            "is_following",
            "is_blocked",
        ]