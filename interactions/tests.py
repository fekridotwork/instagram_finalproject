from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from interactions.models import Comment, Like, SavePost
from posts.models import Post


class InteractionAPITests(APITestCase):
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

    def make_post(self):
        return Post.objects.create(
            user=self.other_user,
            media=self.make_image(),
            media_type="image",
            caption="test post",
            visibility="public",
        )

    def test_user_can_like_post(self):
        post = self.make_post()

        url = reverse("post-like", kwargs={"post_id": post.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(user=self.user, post=post).exists()
        )

    def test_user_can_unlike_post(self):
        post = self.make_post()

        Like.objects.create(
            user=self.user,
            post=post,
        )

        url = reverse("post-like", kwargs={"post_id": post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Like.objects.filter(user=self.user, post=post).exists()
        )

    def test_user_can_save_post(self):
        post = self.make_post()

        url = reverse("post-save", kwargs={"post_id": post.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            SavePost.objects.filter(user=self.user, post=post).exists()
        )

    def test_user_can_unsave_post(self):
        post = self.make_post()

        SavePost.objects.create(
            user=self.user,
            post=post,
        )

        url = reverse("post-save", kwargs={"post_id": post.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            SavePost.objects.filter(user=self.user, post=post).exists()
        )

    def test_user_can_comment_on_post(self):
        post = self.make_post()

        url = reverse("post-comment", kwargs={"post_id": post.id})

        response = self.client.post(
            url,
            data={
                "text": "nice post",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Comment.objects.filter(
                user=self.user,
                post=post,
                text="nice post",
            ).exists()
        )