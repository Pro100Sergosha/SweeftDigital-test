from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import WeightLog
from datetime import date


class WeightLogTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="TestPass123!"
        )
        self.url = reverse("weightlog-list")
        self.client.force_authenticate(user=self.user)

    def test_create_weight_log(self):
        """Test creating a weight log entry"""
        data = {"weight": 75.5}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WeightLog.objects.count(), 1)
        log = WeightLog.objects.first()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.weight, 75.5)
        self.assertEqual(log.date, date.today())
