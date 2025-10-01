from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import Profile


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="TestPass123!"
        )
        self.url = reverse("profile-list")
        self.client.force_authenticate(user=self.user)

    def test_create_profile(self):
        """Test creating a profile for authenticated user"""
        data = {"weight": 75.5, "height": 180.0}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.weight, 75.5)
        self.assertEqual(profile.height, 180.0)

    def test_create_duplicate_profile(self):
        """Test that user cannot create multiple profiles"""
        Profile.objects.create(user=self.user, weight=75.0, height=180.0)
        data = {"weight": 80.0, "height": 185.0}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Profile.objects.count(), 1)

    def test_get_own_profile(self):
        """Test retrieving own profile"""
        profile = Profile.objects.create(user=self.user, weight=75.0, height=180.0)
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["weight"], 75.0)

    def test_cannot_see_other_users_profile(self):
        """Test that users can only see their own profiles"""
        Profile.objects.create(user=self.other_user, weight=80.0, height=175.0)
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_update_profile(self):
        """Test updating own profile"""
        profile = Profile.objects.create(user=self.user, weight=75.0, height=180.0)
        url = reverse("profile-detail", kwargs={"pk": profile.pk})
        data = {"weight": 77.0, "height": 180.0}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.weight, 77.0)

    def test_cannot_update_other_users_profile(self):
        """Test that users cannot update other users' profiles"""
        other_profile = Profile.objects.create(
            user=self.other_user, weight=80.0, height=175.0
        )
        url = reverse("profile-detail", kwargs={"pk": other_profile.pk})
        data = {"weight": 85.0, "height": 175.0}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access profiles"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_profile(self):
        """Test partially updating profile (PATCH)"""
        profile = Profile.objects.create(user=self.user, weight=75.0, height=180.0)
        url = reverse("profile-detail", kwargs={"pk": profile.pk})
        data = {"weight": 76.0}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.weight, 76.0)
        self.assertEqual(profile.height, 180.0)  # Height unchanged

    def test_delete_profile(self):
        """Test deleting own profile"""
        profile = Profile.objects.create(user=self.user, weight=75.0, height=180.0)
        url = reverse("profile-detail", kwargs={"pk": profile.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profile.objects.count(), 0)
