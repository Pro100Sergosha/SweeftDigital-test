from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import WorkoutPlan, Exercise, WorkoutExercise


class WorkoutExerciseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        self.url = reverse("workoutexercise-list")
        self.client.force_authenticate(user=self.user)
        
        # Create exercises
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
        
        # Create workout plan
        self.workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            title="Test Plan",
            goal="Strength",
            frequency_per_week=3,
            session_duration_minutes=60,
        )

    def test_add_exercise_to_workout_plan(self):
        """Test adding an exercise to a workout plan"""
        data = {
            "workout_plan": self.workout_plan.id,
            "exercise_id": self.exercise1.id,
            "sets": 3,
            "repetitions": 12,
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutExercise.objects.count(), 1)
        workout_exercise = WorkoutExercise.objects.first()
        self.assertEqual(workout_exercise.exercise, self.exercise1)
        self.assertEqual(workout_exercise.sets, 3)
        self.assertEqual(workout_exercise.repetitions, 12)

    def test_add_exercise_with_duration(self):
        """Test adding an exercise with duration instead of repetitions"""
        data = {
            "workout_plan": self.workout_plan.id,
            "exercise_id": self.exercise1.id,
            "sets": 3,
            "duration_seconds": 60,
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        workout_exercise = WorkoutExercise.objects.first()
        self.assertEqual(workout_exercise.duration_seconds, 60)
        self.assertIsNone(workout_exercise.repetitions)

    def test_add_exercise_with_distance(self):
        """Test adding an exercise with distance"""
        data = {
            "workout_plan": self.workout_plan.id,
            "exercise_id": self.exercise1.id,
            "sets": 1,
            "distance_meters": 5000,
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        workout_exercise = WorkoutExercise.objects.first()
        self.assertEqual(workout_exercise.distance_meters, 5000)

    def test_list_workout_exercises(self):
        """Test listing all workout exercises"""
        WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise2,
            sets=4,
            repetitions=10,
        )
        
        response = self.client.get(self.url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_workout_exercise(self):
        """Test retrieving a specific workout exercise"""
        workout_exercise = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        url = reverse("workoutexercise-detail", kwargs={"pk": workout_exercise.pk})
        response = self.client.get(url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sets"], 3)
        self.assertEqual(response.data["repetitions"], 12)
        self.assertEqual(response.data["exercise"]["name"], "Push Ups")

    def test_update_workout_exercise(self):
        """Test updating a workout exercise"""
        workout_exercise = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        url = reverse("workoutexercise-detail", kwargs={"pk": workout_exercise.pk})
        data = {
            "workout_plan": self.workout_plan.id,
            "exercise_id": self.exercise1.id,
            "sets": 4,
            "repetitions": 15,
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workout_exercise.refresh_from_db()
        self.assertEqual(workout_exercise.sets, 4)
        self.assertEqual(workout_exercise.repetitions, 15)

    def test_delete_workout_exercise(self):
        """Test deleting a workout exercise"""
        workout_exercise = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        url = reverse("workoutexercise-detail", kwargs={"pk": workout_exercise.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(WorkoutExercise.objects.count(), 0)

    def test_change_exercise_in_workout(self):
        """Test changing the exercise in a workout exercise"""
        workout_exercise = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        url = reverse("workoutexercise-detail", kwargs={"pk": workout_exercise.pk})
        data = {
            "workout_plan": self.workout_plan.id,
            "exercise_id": self.exercise2.id,
            "sets": 3,
            "repetitions": 12,
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workout_exercise.refresh_from_db()
        self.assertEqual(workout_exercise.exercise, self.exercise2)

    def test_partial_update_workout_exercise(self):
        """Test partially updating workout exercise (PATCH)"""
        workout_exercise = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        url = reverse("workoutexercise-detail", kwargs={"pk": workout_exercise.pk})
        data = {"sets": 5}
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workout_exercise.refresh_from_db()
        self.assertEqual(workout_exercise.sets, 5)
        self.assertEqual(workout_exercise.repetitions, 12)  # Unchanged

    def test_unauthenticated_cannot_add_exercise(self):
        """Test that unauthenticated users cannot add exercises to workout plans"""
        self.client.force_authenticate(user=None)
        data = {
            "workout_plan": self.workout_plan.id,
            "exercise_id": self.exercise1.id,
            "sets": 3,
            "repetitions": 12,
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
