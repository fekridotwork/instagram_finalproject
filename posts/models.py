from django.db import models
from datetime import timedelta
from django.utils import timezone

MEDIA_TYPE_CHOICES = [
    ('image', 'Image'),
    ('video', 'Video'),
]
VISIBILITY_CHOICES = [
    ('public', 'Public'),
    ('followers', 'Followers'),
]

class Post(models.Model):

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    hashtags = models.ManyToManyField(
        "posts.Hashtag",
        through="posts.PostHashtag",
        related_name="posts",
        blank=True,
    )
    media = models.FileField(
        upload_to="posts/",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
    )
    caption = models.TextField(
        blank=True,
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public',
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    is_edited = models.BooleanField(
        default=False,
    )

    comments_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post #{self.pk} by {self.user}"

def story_expiry():
    return timezone.now() + timedelta(hours=24)

class Story(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="stories",
    )
    media = models.FileField(
        upload_to="stories/",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
    )
    text = models.TextField(
        blank=True,
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='followers',
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    expires_at = models.DateTimeField(
        default=story_expiry,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"Story #{self.pk} by {self.user}"

class Hashtag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name

class PostHashtag(models.Model):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="post_hashtags",
    )
    hashtag = models.ForeignKey(
        "posts.Hashtag",
        on_delete=models.CASCADE,
        related_name="post_hashtags",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "hashtag"],
                name="unique_post_hashtag",
            )
        ]
    def __str__(self):
        return f"Post #{self.post_id} --> #{self.hashtag.name}"