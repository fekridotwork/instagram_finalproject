from django.db import models
from django.utils import timezone


class DirectConversation(models.Model):
    user1 = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="direct_conversations_as_user1"
    )
    user2 = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="direct_conversations_as_user2"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(user1=models.F("user2")),
                name="prevent_self_conversation"
            ),
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_direct_conversation_pair"
            )
        ]
    def __str__(self):
        return f"Conversation #{self.pk}: {self.user1} & {self.user2}"
class DirectMessage(models.Model):
    conversation = models.ForeignKey(
        "direct.DirectConversation",
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sent_directz_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"], name="dm_conv_created_idx"),
            models.Index(fields=["sender", "created_at"], name="dm_sender_created_idx"),
        ]
    def __str__(self):
        return f"Direct Message #{self.pk}: {self.sender} & {self.text}"