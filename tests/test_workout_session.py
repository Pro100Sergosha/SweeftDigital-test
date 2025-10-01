from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import (
    WorkoutPlan,
    Exercise,
    WorkoutExercise,
    WorkoutSession,
    SessionExercise,
    SetLog,
)


class WorkoutSessionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
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

        # Create workout plan with exercises
        self.workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            title="Test Workout",
            goal="Strength",
            frequency_per_week=3,
            session_duration_minutes=60,
        )
        self.workout_ex1 = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise1,
            sets=3,
            repetitions=12,
        )
        self.workout_ex2 = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=self.exercise2,
            sets=4,
            repetitions=10,
        )

        self.session_url = reverse("workoutsession-list")

    def test_start_workout_session(self):
        """Test starting a new workout session"""
        url = reverse("workoutsession-start-session")
        data = {"workout_plan_id": self.workout_plan.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutSession.objects.count(), 1)

        session = WorkoutSession.objects.first()
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.status, "in_progress")
        self.assertEqual(session.session_exercises.count(), 2)

        # Check that set logs were created
        for session_ex in session.session_exercises.all():
            self.assertEqual(session_ex.set_logs.count(), session_ex.planned_sets)

    def test_cannot_start_multiple_sessions(self):
        """Test that user cannot have multiple active sessions"""
        url = reverse("workoutsession-start-session")
        data = {"workout_plan_id": self.workout_plan.id}

        # Start first session
        self.client.post(url, data, format="json")

        # Try to start second session
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(WorkoutSession.objects.count(), 1)

    def test_get_active_session(self):
        """Test retrieving the active workout session"""
        # Start a session
        url = reverse("workoutsession-start-session")
        data = {"workout_plan_id": self.workout_plan.id}
        self.client.post(url, data, format="json")

        # Get active session
        active_url = reverse("workoutsession-active-session")
        response = self.client.get(active_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["session_exercises"][0]["exercise_name"], "Push Ups"
        )

    def test_update_session_exercise_status(self):
        """Test updating the status of a session exercise"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )
        session_ex = SessionExercise.objects.create(
            session=session,
            workout_exercise=self.workout_ex1,
            order=0,
            planned_sets=3,
            planned_repetitions=12,
            status="pending",
        )

        url = reverse("sessionexercise-update-status", kwargs={"pk": session_ex.pk})
        data = {"status": "in_progress", "notes": "Starting now"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session_ex.refresh_from_db()
        self.assertEqual(session_ex.status, "in_progress")
        self.assertIsNotNone(session_ex.started_at)

    def test_complete_set(self):
        """Test completing a set"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )
        session_ex = SessionExercise.objects.create(
            session=session,
            workout_exercise=self.workout_ex1,
            order=0,
            planned_sets=3,
            planned_repetitions=12,
        )
        set_log = SetLog.objects.create(
            session_exercise=session_ex,
            set_number=1,
        )

        url = reverse("setlog-complete-set", kwargs={"pk": set_log.pk})
        data = {
            "repetitions": 12,
            "weight_kg": 20.0,
            "rest_seconds": 90,
            "notes": "Felt good",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        set_log.refresh_from_db()
        self.assertTrue(set_log.completed)
        self.assertEqual(set_log.repetitions, 12)
        self.assertEqual(set_log.weight_kg, 20.0)
        self.assertIsNotNone(set_log.completed_at)

    def test_cannot_complete_set_twice(self):
        """Test that a set cannot be completed twice"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )
        session_ex = SessionExercise.objects.create(
            session=session,
            workout_exercise=self.workout_ex1,
            order=0,
            planned_sets=3,
            planned_repetitions=12,
        )
        set_log = SetLog.objects.create(
            session_exercise=session_ex,
            set_number=1,
            completed=True,
        )

        url = reverse("setlog-complete-set", kwargs={"pk": set_log.pk})
        data = {"repetitions": 12}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_next_set(self):
        """Test getting the next set to perform"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )
        session_ex = SessionExercise.objects.create(
            session=session,
            workout_exercise=self.workout_ex1,
            order=0,
            planned_sets=3,
            planned_repetitions=12,
        )
        SetLog.objects.create(
            session_exercise=session_ex,
            set_number=1,
            completed=True,
        )
        SetLog.objects.create(
            session_exercise=session_ex,
            set_number=2,
            completed=False,
        )

        url = reverse("sessionexercise-next-set", kwargs={"pk": session_ex.pk})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["set_number"], 2)

    def test_auto_complete_exercise_after_all_sets(self):
        """Test that exercise is auto-completed after all sets are done"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )
        session_ex = SessionExercise.objects.create(
            session=session,
            workout_exercise=self.workout_ex1,
            order=0,
            planned_sets=2,
            planned_repetitions=12,
            status="in_progress",
        )
        set1 = SetLog.objects.create(
            session_exercise=session_ex,
            set_number=1,
        )
        set2 = SetLog.objects.create(
            session_exercise=session_ex,
            set_number=2,
        )

        # Complete first set
        url = reverse("setlog-complete-set", kwargs={"pk": set1.pk})
        self.client.post(url, {"repetitions": 12}, format="json")

        # Complete second set
        url = reverse("setlog-complete-set", kwargs={"pk": set2.pk})
        self.client.post(url, {"repetitions": 12}, format="json")

        # Check that exercise is marked as completed
        session_ex.refresh_from_db()
        self.assertEqual(session_ex.status, "completed")
        self.assertEqual(session_ex.completed_sets, 2)
        self.assertIsNotNone(session_ex.completed_at)

    def test_list_user_sessions(self):
        """Test listing workout sessions for a user"""
        WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="completed"
        )
        WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )

        response = self.client.get(self.session_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_unauthenticated_cannot_start_session(self):
        """Test that unauthenticated users cannot start sessions"""
        self.client.force_authenticate(user=None)
        url = reverse("workoutsession-start-session")
        data = {"workout_plan_id": self.workout_plan.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_session_with_duration_exercise(self):
        """Test session with duration-based exercises"""
        plank = Exercise.objects.create(
            name="Plank",
            description="Core exercise",
            instructions="Hold position",
            target_muscles="core",
            equipment="bodyweight",
        )
        workout_ex = WorkoutExercise.objects.create(
            workout_plan=self.workout_plan,
            exercise=plank,
            sets=3,
            duration_seconds=60,
        )

        url = reverse("workoutsession-start-session")
        data = {"workout_plan_id": self.workout_plan.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session = WorkoutSession.objects.first()

        # Find the plank exercise in session
        plank_session_ex = session.session_exercises.filter(
            workout_exercise=workout_ex
        ).first()
        self.assertEqual(plank_session_ex.planned_duration_seconds, 60)
        self.assertIsNone(plank_session_ex.planned_repetitions)
        self.assertEqual(response.data["status"], "in_progress")

    def test_get_active_session_when_none(self):
        """Test retrieving active session when there is none"""
        url = reverse("workoutsession-active-session")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_complete_workout_session(self):
        """Test completing a workout session"""
        # Start session
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )

        # Complete session
        url = reverse("workoutsession-complete-session", kwargs={"pk": session.pk})
        data = {"notes": "Great workout!"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(session.status, "completed")
        self.assertIsNotNone(session.completed_at)
        self.assertEqual(session.notes, "Great workout!")
        self.assertIsNotNone(session.total_duration_minutes)

    def test_cancel_workout_session(self):
        """Test cancelling a workout session"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )

        url = reverse("workoutsession-cancel-session", kwargs={"pk": session.pk})
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(session.status, "cancelled")

    def test_get_next_exercise(self):
        """Test getting the next exercise in a session"""
        session = WorkoutSession.objects.create(
            user=self.user, workout_plan=self.workout_plan, status="in_progress"
        )
        SessionExercise.objects.create(
            session=session,
            workout_exercise=self.workout_ex1,
            order=0,
            planned_sets=3,
            planned_repetitions=12,
            status="pending",
        )

        url = reverse("workoutsession-next-exercise", kwargs={"pk": session.pk})
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exercise_name"], "Push Ups")
