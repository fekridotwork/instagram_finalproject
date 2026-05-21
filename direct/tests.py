from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from direct.models import DirectConversation, DirectMessage


class DirectAPITests(APITestCase):
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

    def test_user_can_create_conversation(self):
        url = reverse("conversation-list-create")

        response = self.client.post(
            url,
            data={"user_id": self.other_user.id},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DirectConversation.objects.count(), 1)

    def test_duplicate_conversation_is_not_created(self):
        DirectConversation.objects.create(
            user1=self.user,
            user2=self.other_user,
        )

        url = reverse("conversation-list-create")

        response = self.client.post(
            url,
            data={"user_id": self.other_user.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DirectConversation.objects.count(), 1)

    def test_user_can_send_message(self):
        conversation = DirectConversation.objects.create(
            user1=self.user,
            user2=self.other_user,
        )

        url = reverse(
            "conversation-messages",
            kwargs={"conversation_id": conversation.id},
        )

        response = self.client.post(
            url,
            data={"text": "hello"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DirectMessage.objects.count(), 1)
        self.assertEqual(DirectMessage.objects.first().sender, self.user)

    def test_user_can_get_conversation_messages(self):
        conversation = DirectConversation.objects.create(
            user1=self.user,
            user2=self.other_user,
        )

        DirectMessage.objects.create(
            conversation=conversation,
            sender=self.user,
            text="hello",
        )

        url = reverse(
            "conversation-messages",
            kwargs={"conversation_id": conversation.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "hello")

    def test_user_can_get_inbox(self):
        conversation = DirectConversation.objects.create(
            user1=self.user,
            user2=self.other_user,
        )

        DirectMessage.objects.create(
            conversation=conversation,
            sender=self.other_user,
            text="hi matin",
        )

        url = reverse("conversation-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "hi matin")