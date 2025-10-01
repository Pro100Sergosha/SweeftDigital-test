from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User


class SimpleRegisterTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")
        self.user = User.objects.create_user(
            username="admin", email="admin@gmail.com", password="Qwerty1234@"
        )
        self.valid_data = {
            "username": "sergo",
            "email": "sergo@example.com",
            "password": "Strong#123",
            "confirm_password": "Strong#123",
        }
        self.exist_data = {
            "username": "admin",
            "email": "admin@gmail.com",
            "password": "Qwerty1234@",
            "confirm_password": "Qwerty1234@",
        }

    def test_register_valid_data(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.valid_data["email"])
        self.assertEqual(user.username, self.valid_data["username"])
        self.assertTrue(user.check_password(self.valid_data["password"]))

    def test_passwords_do_not_match(self):
        data = self.valid_data.copy()
        data["confirm_password"] = "Wrong#123"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_weak_password(self):
        data = self.valid_data.copy()
        data["password"] = data["confirm_password"] = "abc"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_invalid_email(self):
        data = self.valid_data.copy()
        data["email"] = "not-an-email"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_missing_username(self):
        data = self.valid_data.copy()
        del data["username"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_username(self):
        response = self.client.post(self.url, self.exist_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_email(self):
        response = self.client.post(self.url, self.exist_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
