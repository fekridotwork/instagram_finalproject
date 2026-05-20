from interactions.models import Block, Follow


def block_user(blocker, blocked):
    if blocker == blocked:
        raise ValueError("You cannot block yourself.")

    Block.objects.get_or_create(
        blocker=blocker,
        blocked=blocked,
    )

    Follow.objects.filter(
        follower=blocker,
        following=blocked,
    ).delete()

    Follow.objects.filter(
        follower=blocked,
        following=blocker,
    ).delete()


def unblock_user(blocker, blocked):
    Block.objects.filter(
        blocker=blocker,
        blocked=blocked,
    ).delete()

def is_blocked_between(user1, user2):
    if not user1 or not user2:
        return False

    if not user1.is_authenticated or not user2.is_authenticated:
        return False

    return Block.objects.filter(
        blocker=user1,
        blocked=user2,
    ).exists() or Block.objects.filter(
        blocker=user2,
        blocked=user1,
    ).exists()