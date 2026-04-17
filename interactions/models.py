from django.db import models

class Follow(models.Model):
    follower = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="following_relations",
    )
    following = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="follower_relations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow_relation",
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            )
        ]
    def __str__(self):
        return f"{self.follower} -> {self.following}"
class Like(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="given_likes",
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="received_likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like",
            )
        ]
    def __str__(self):
        return f"{self.user} liked post #{self.post.id}"

class Comment(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True
    )
    text = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        models.CheckConstraint(
            condition=~models.Q(parent=models.F("id")),
            name="prevent_self_parent_comment",
        )
        indexes = [
            models.Index(fields=["post", "created_at"], name="comment_post_created_idx"),
            models.Index(fields=["user", "created_at"], name="comment_user_created_idx"),
        ]
    def __str__(self):
        return f"{self.user} commented on #{self.post.id}"