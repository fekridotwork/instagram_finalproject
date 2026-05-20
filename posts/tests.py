from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from interactions.models import Follow
from posts.models import Post


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