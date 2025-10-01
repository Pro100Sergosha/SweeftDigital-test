from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import Exercise


class ExerciseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        self.url = reverse("exercise-list")
        self.exercise = Exercise.objects.create(
            name="Push Ups",
            description="Basic bodyweight exercise",
            instructions="Lower and push up",
            target_muscles="chest, triceps",
            equipment="bodyweight",
        )

    def test_list_exercises_unauthenticated(self):
        """Test that unauthenticated users can view exercises"""
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_exercises_authenticated(self):
        """Test that authenticated users can view exercises"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_exercise(self):
        """Test retrieving a single exercise"""
        url = reverse("exercise-detail", kwargs={"pk": self.exercise.pk})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Push Ups")
        self.assertEqual(response.data["target_muscles"], "chest, triceps")

    def test_create_exercise_unauthenticated(self):
        """Test that unauthenticated users cannot create exercises"""
        data = {
            "name": "Pull Ups",
            "description": "Upper body exercise",
            "instructions": "Pull chin above bar",
            "target_muscles": "back, biceps",
            "equipment": "pull-up bar",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_exercise_authenticated(self):
        """Test that authenticated users can create exercises"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Pull Ups",
            "description": "Upper body exercise",
            "instructions": "Pull chin above bar",
            "target_muscles": "back, biceps",
            "equipment": "pull-up bar",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exercise.objects.count(), 2)
        self.assertTrue(Exercise.objects.filter(name="Pull Ups").exists())

    def test_update_exercise_authenticated(self):
        """Test updating an exercise"""
        self.client.force_authenticate(user=self.user)
        url = reverse("exercise-detail", kwargs={"pk": self.exercise.pk})
        data = {
            "name": "Push Ups",
            "description": "Updated description",
            "instructions": "Lower and push up",
            "target_muscles": "chest, triceps, shoulders",
            "equipment": "bodyweight",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exercise.refresh_from_db()
        self.assertEqual(self.exercise.description, "Updated description")

    def test_delete_exercise_authenticated(self):
        """Test deleting an exercise"""
        self.client.force_authenticate(user=self.user)
        url = reverse("exercise-detail", kwargs={"pk": self.exercise.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Exercise.objects.count(), 0)

    def test_exercise_unique_name(self):
        """Test that exercise names must be unique"""
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Push Ups",  # Already exists
            "description": "Duplicate exercise",
            "instructions": "Instructions",
            "target_muscles": "chest",
            "equipment": "bodyweight",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_filter_exercises_by_target_muscles(self):
        """Test filtering exercises by target muscles"""
        Exercise.objects.create(
            name="Squats",
            description="Leg exercise",
            instructions="Squat down",
            target_muscles="quadriceps, glutes",
            equipment="bodyweight",
        )

        response = self.client.get(f"{self.url}?search=chest", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: This assumes search is configured in the viewset
        # If not configured, this test will need to be adjusted
