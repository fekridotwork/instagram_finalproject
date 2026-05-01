def can_view_post(user, post) -> bool:
    if post.user == user:
        return True

    if post.user.profile.is_private:
        return False

    if post.visibility == "followers":
        return False

    return True