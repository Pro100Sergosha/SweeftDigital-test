from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import WorkoutPlan, Exercise, WorkoutExercise


class WorkoutPlanTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="TestPass123!"
        )
        self.url = reverse("workoutplan-list")
        self.client.force_authenticate(user=self.user)
        
        # Create some exercises
        self.exercise1 = Exercise.objects.create(
            name="Push Ups",
            description="Chest exercise",
            instructions="Lower and push",
            target_muscles="chest, triceps",
            equipment="bodyweight",
        )
        self.exercise2 = Exercise.objects.create(
            name="Squats",
            description="Leg exercise",
            instructions="Squat down",
            target_muscles="quadriceps, glutes",
            equipment="bodyweight",
        )

    def test_create_workout_plan(self):
        """Test creating a workout plan"""
        data = {
            "title": "Beginner Strength Training",
            "goal": "Build muscle",
            "frequency_per_week": 3,
            "session_duration_minutes": 45,
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutPlan.objects.count(), 1)
        plan = WorkoutPlan.objects.first()
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.title, "Beginner Strength Training")

    def test_list_own_workout_plans(self):
        """Test that users only see their own workout plans"""
        WorkoutPlan.objects.create(
            user=self.user,
            title="My Plan",
            goal="Strength",
            frequency_per_week=3,
            session_duration_minutes=60,
        )
        WorkoutPlan.objects.create(
            user=self.other_user,
            title="Other's Plan",
            goal="Cardio",
            frequency_per_week=5,
            session_duration_minutes=30,
        )
        
        response = self.client.get(self.url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "My Plan")

    def test_retrieve_workout_plan(self):
        """Test retrieving a specific workout plan"""
        plan = WorkoutPlan.objects.create(
            user=self.user,
            title="Test Plan",
            goal="Fitness",
            frequency_per_week=4,
            session_duration_minutes=50,
        )
        url = reverse("workoutplan-detail", kwargs={"pk": plan.pk})
        response = self.client.get(url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Plan")
        self.assertEqual(response.data["frequency_per_week"], 4)

    def test_update_workout_plan(self):
        """Test updating a workout plan"""
        plan = WorkoutPlan.objects.create(
            user=self.user,
            title="Original Plan",
            goal="Strength",
            frequency_per_week=3,
            session_duration_minutes=60,
        )
        url = reverse("workoutplan-detail", kwargs={"pk": plan.pk})
        data = {
            "title": "Updated Plan",
            "goal": "Endurance",
            "frequency_per_week": 5,
            "session_duration_minutes": 45,
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        plan.refresh_from_db()
        self.assertEqual(plan.title, "Updated Plan")
        self.assertEqual(plan.goal, "Endurance")

    def test_delete_workout_plan(self):
        """Test deleting a workout plan"""
        plan = WorkoutPlan.objects.create(
            user=self.user,
            title="To Delete",
            goal="Test",
            frequency_per_week=3,
            session_duration_minutes=60,
        )
        url = reverse("workoutplan-detail", kwargs={"pk": plan.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(WorkoutPlan.objects.count(), 0)

    def test_workout_plan_with_exercises(self):
        """Test creating a workout plan and viewing its exercises"""
        plan = WorkoutPlan.objects.create(
            user=self.user,
            title="Full Body Workout",
            goal="Strength",
            frequency_per_week=3,
            session_duration_minutes=60,
        )
        WorkoutExercise.objects.create(
            workout_plan=plan, exercise=self.exercise1, sets=3, repetitions=12
        )
        WorkoutExercise.objects.create(
            workout_plan=plan, exercise=self.exercise2, sets=4, repetitions=10
        )
        
        url = reverse("workoutplan-detail", kwargs={"pk": plan.pk})
        response = self.client.get(url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["exercises"]), 2)
        self.assertEqual(response.data["exercises"][0]["exercise"]["name"], "Push Ups")

    def test_unauthenticated_cannot_create_plan(self):
        """Test that unauthenticated users cannot create workout plans"""
        self.client.force_authenticate(user=None)
        data = {
            "title": "Test Plan",
            "goal": "Fitness",
            "frequency_per_week": 3,
            "session_duration_minutes": 60,
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_access_other_users_plan(self):
        """Test that users cannot access other users' workout plans"""
        other_plan = WorkoutPlan.objects.create(
            user=self.other_user,
            title="Other's Plan",
            goal="Cardio",
            frequency_per_week=5,
            session_duration_minutes=30,
        )
        url = reverse("workoutplan-detail", kwargs={"pk": other_plan.pk})
        response = self.client.get(url, format="json")
        
        # Should return 404 because it's filtered out by get_queryset
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_workout_plan(self):
        """Test partially updating workout plan (PATCH)"""
        plan = WorkoutPlan.objects.create(
            user=self.user,
            title="Original",
            goal="Strength",
            frequency_per_week=3,
            session_duration_minutes=60,
        )
        url = reverse("workoutplan-detail", kwargs={"pk": plan.pk})
        data = {"frequency_per_week": 5}
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        plan.refresh_from_db()
        self.assertEqual(plan.frequency_per_week, 5)
        self.assertEqual(plan.title, "Original")  # Unchanged
