from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from authentication.services import redis_client, store_otp


class AuthAPITests(APITestCase):
    def setUp(self):
        redis_client.flushdb()

    def test_user_can_request_login_otp(self):
        User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )

        url = reverse("request_otp")

        response = self.client.post(
            url,
            data={
                "identifier": "matin@example.com",
                "purpose": "login",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_otp_for_unknown_user_fails(self):
        url = reverse("request_otp")

        response = self.client.post(
            url,
            data={
                "identifier": "ghost@example.com",
                "purpose": "login",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_verify_valid_otp(self):
        User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )

        identifier = "matin@example.com"

        store_otp(identifier, "login", "12345")

        url = reverse("verify_otp")

        response = self.client.post(
            url,
            data={
                "identifier": identifier,
                "purpose": "login",
                "code": "12345",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_otp_fails(self):
        User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )

        identifier = "matin@example.com"

        store_otp(identifier, "login", "12345")

        url = reverse("verify_otp")

        response = self.client.post(
            url,
            data={
                "identifier": identifier,
                "purpose": "login",
                "code": "00000",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_otp_fails(self):
        User.objects.create_user(
            username="matin",
            email="matin@example.com",
            password="testpass123",
        )

        url = reverse("verify_otp")

        response = self.client.post(
            url,
            data={
                "identifier": "matin@example.com",
                "purpose": "login",
                "code": "12345",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)