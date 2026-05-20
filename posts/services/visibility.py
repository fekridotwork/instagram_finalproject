from interactions.models import Follow
from interactions.services import is_blocked_between


def is_following(user, target_user):
    if not user or not user.is_authenticated:
        return False

    if user == target_user:
        return True

    return Follow.objects.filter(
        follower=user,
        following=target_user,
    ).exists()


def can_view_profile(user, target_user):
    if not target_user.is_active:
        return False

    if user == target_user:
        return True
    
    if is_blocked_between(user, target_user):
        return False

    if not target_user.profile.is_private:
        return True

    return is_following(user, target_user)


def can_view_content(user, content):
    if content.is_deleted:
        return False

    if content.user == user:
        return True
    
    if is_blocked_between(user, content.user):
        return False

    is_follower = is_following(user, content.user)

    if content.user.profile.is_private:
        return is_follower

    if content.visibility == "public":
        return True

    if content.visibility == "followers":
        return is_follower

    return False


def can_view_post(user, post):
    return can_view_content(user, post)


def can_view_story(user, story):
    return can_view_content(user, story)