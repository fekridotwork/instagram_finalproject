from datetime import timedelta
from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from interactions.models import Follow
from posts.models import Post, Story


class PostAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="ali",
            email="ali@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=self.user)

    def make_image(self):
        image = Image.new("RGB", (10, 10), color="white")
        image_file = BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(
            name="test.jpg",
            content=image_file.read(),
            content_type="image/jpeg",
        )

    def test_authenticated_user_can_create_post(self):
        url = reverse("post-list")

        response = self.client.post(
            url,
            data={
                "media": self.make_image(),
                "media_type": "image",
                "caption": "test caption",
                "visibility": "public",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().user, self.user)

    def test_user_can_see_public_post_detail(self):
        post = Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="public post",
            visibility="public",
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], post.id)

    def test_user_cannot_update_other_users_post(self):
        post = Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="other post",
            visibility="public",
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})

        response = self.client.patch(
            url,
            data={"caption": "hacked caption"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        post.refresh_from_db()
        self.assertEqual(post.caption, "other post")

    def test_owner_can_soft_delete_post(self):
        post = Post.objects.create(
            user=self.user,
            media=self.make_image(),
            media_type="image",
            caption="my post",
            visibility="public",
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        post.refresh_from_db()
        self.assertTrue(post.is_deleted)
    
    def test_unauthenticated_user_cannot_create_post(self):
        self.client.force_authenticate(user=None)

        url = reverse("post-list")

        response = self.client.post(
            url,
            data={
                "media": self.make_image(),
                "media_type": "image",
                "caption": "test",
                "visibility": "public",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_own_post(self):
        post = Post.objects.create(
            user=self.user,
            media=self.make_image(),
            media_type="image",
            caption="old caption",
            visibility="public",
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})

        response = self.client.patch(
            url,
            data={
                "caption": "new caption",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post.refresh_from_db()
        self.assertEqual(post.caption, "new caption")

    def test_deleted_post_should_not_be_accessible(self):
        post = Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="deleted",
            visibility="public",
            is_deleted=True,
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_follower_cannot_see_followers_only_post(self):
        post = Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="followers only post",
            visibility="followers",
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_follower_can_see_followers_only_post(self):
        Follow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        post = Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="followers only post",
            visibility="followers",
        )

        url = reverse("post-detail", kwargs={"post_id": post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], post.id)

class StoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="ali",
            email="ali@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def make_image(self):
        image = Image.new("RGB", (10, 10), color="white")
        image_file = BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(
            name="story.jpg",
            content=image_file.read(),
            content_type="image/jpeg",
        )

    def test_user_can_create_image_story(self):
        url = reverse("story-create")

        response = self.client.post(
            url,
            data={
                "media": self.make_image(),
                "media_type": "image",
                "text": "my story",
                "visibility": "followers",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.first().user, self.user)

    def test_user_can_create_text_story(self):
        url = reverse("story-create")

        response = self.client.post(
            url,
            data={
                "media_type": "text",
                "text": "text only story",
                "visibility": "followers",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Story.objects.count(), 1)

    def test_user_can_see_followed_users_story(self):
        Follow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        Story.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            text="visible story",
            visibility="followers",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        url = reverse("story-feed")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "visible story")
    def test_expired_story_is_not_visible(self):
        Follow.objects.create(
            follower=self.user,
            following=self.other_user,
        )

        Story.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            text="expired story",
            visibility="followers",
            expires_at=timezone.now() - timedelta(hours=1),
        )

        url = reverse("story-feed")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(response, "expired story")

class SearchAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="ali",
            email="ali@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def make_image(self):
        image = Image.new("RGB", (10, 10), color="white")
        image_file = BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)

        return SimpleUploadedFile(
            name="post.jpg",
            content=image_file.read(),
            content_type="image/jpeg",
        )

    def test_user_can_search_users(self):
        url = reverse("global-search")

        response = self.client.get(
            url,
            {
                "search": "ali",
                "type": "users",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["users"]), 1)
        self.assertEqual(response.data["posts"], [])

    def test_empty_search_returns_empty_results(self):
        url = reverse("global-search")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["users"], [])
        self.assertEqual(response.data["posts"], [])

    def test_invalid_search_type_returns_400(self):
        url = reverse("global-search")

        response = self.client.get(
            url,
            {
                "search": "django",
                "type": "wrong",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_search_posts_by_hashtag(self):
        post = Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="Learning Django #django",
            visibility="public",
        )

        # چون توی perform_create هشتگ sync می‌کنی، اما اینجا مستقیم model ساختیم،
        # باید خودمان بعداً اگر تست fail شد sync را صدا بزنیم.
        from posts.services.hashtags import sync_post_hashtags
        sync_post_hashtags(post)

        url = reverse("global-search")

        response = self.client.get(
            url,
            {
                "search": "django",
                "type": "posts",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["users"], [])
        self.assertEqual(len(response.data["posts"]), 1)