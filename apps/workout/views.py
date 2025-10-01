from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from .models import (
    Profile,
    Exercise,
    WorkoutPlan,
    WorkoutExercise,
    WeightLog,
    FitnessGoal,
)
from .serializers import (
    ProfileSerializer,
    ExerciseSerializer,
    WorkoutPlanSerializer,
    WorkoutExerciseSerializer,
    WeightLogSerializer,
    FitnessGoalSerializer,
)


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    WorkoutSession,
    SessionExercise,
    SetLog,
    WorkoutPlan,
    WorkoutExercise,
)
from .serializers import *


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    queryset = WorkoutSession.objects.all()
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="start")
    def start_session(self, request):
        """Start a new workout session"""
        serializer = StartWorkoutSessionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        workout_plan_id = serializer.validated_data["workout_plan_id"]
        workout_plan = WorkoutPlan.objects.get(id=workout_plan_id)

        # Create the workout session
        session = WorkoutSession.objects.create(
            user=request.user, workout_plan=workout_plan, status="in_progress"
        )

        # Create session exercises from workout plan
        workout_exercises = workout_plan.exercises.all().order_by("id")
        for index, workout_exercise in enumerate(workout_exercises):
            session_exercise = SessionExercise.objects.create(
                session=session,
                workout_exercise=workout_exercise,
                order=index,
                planned_sets=workout_exercise.sets,
                planned_repetitions=workout_exercise.repetitions,
                planned_duration_seconds=workout_exercise.duration_seconds,
                planned_distance_meters=workout_exercise.distance_meters,
            )

            # Create set logs for each planned set
            for set_num in range(1, workout_exercise.sets + 1):
                SetLog.objects.create(
                    session_exercise=session_exercise,
                    set_number=set_num,
                )

        response_serializer = WorkoutSessionSerializer(session)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_session(self, request, pk=None):
        """Complete a workout session"""
        session = self.get_object()

        if session.status != "in_progress":
            return Response(
                {"error": "Session is not in progress"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CompleteSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session.status = "completed"
        session.completed_at = timezone.now()
        session.notes = serializer.validated_data.get("notes", "")

        # Calculate total duration in minutes
        duration = (session.completed_at - session.started_at).total_seconds() / 60
        session.total_duration_minutes = int(duration)

        session.save()

        response_serializer = WorkoutSessionSerializer(session)
        return Response(response_serializer.data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_session(self, request, pk=None):
        """Cancel a workout session"""
        session = self.get_object()

        if session.status != "in_progress":
            return Response(
                {"error": "Session is not in progress"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.status = "cancelled"
        session.completed_at = timezone.now()
        session.save()

        response_serializer = WorkoutSessionSerializer(session)
        return Response(response_serializer.data)

    @action(detail=False, methods=["get"], url_path="active")
    def active_session(self, request):
        """Get the current active workout session"""
        session = WorkoutSession.objects.filter(
            user=request.user, status="in_progress"
        ).first()

        if not session:
            return Response(
                {"message": "No active workout session"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WorkoutSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="next-exercise")
    def next_exercise(self, request, pk=None):
        """Get the next exercise to perform in the session"""
        session = self.get_object()

        if session.status != "in_progress":
            return Response(
                {"error": "Session is not in progress"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find the next pending or in-progress exercise
        next_ex = session.session_exercises.filter(
            status__in=["pending", "in_progress"]
        ).first()

        if not next_ex:
            return Response(
                {"message": "All exercises completed!"}, status=status.HTTP_200_OK
            )

        serializer = SessionExerciseDetailSerializer(next_ex)
        return Response(serializer.data)


class SessionExerciseViewSet(viewsets.ModelViewSet):
    queryset = SessionExercise.objects.all()
    serializer_class = SessionExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SessionExercise.objects.filter(session__user=self.request.user)

    @action(detail=True, methods=["patch"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Update the status of a session exercise"""
        session_exercise = self.get_object()

        serializer = UpdateSessionExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        session_exercise.status = new_status
        session_exercise.notes = serializer.validated_data.get(
            "notes", session_exercise.notes
        )

        if new_status == "in_progress" and not session_exercise.started_at:
            session_exercise.started_at = timezone.now()
        elif (
            new_status in ["completed", "skipped"] and not session_exercise.completed_at
        ):
            session_exercise.completed_at = timezone.now()

        session_exercise.save()

        response_serializer = SessionExerciseDetailSerializer(session_exercise)
        return Response(response_serializer.data)

    @action(detail=True, methods=["get"], url_path="next-set")
    def next_set(self, request, pk=None):
        """Get the next set to perform"""
        session_exercise = self.get_object()

        # Find the first incomplete set
        next_set = session_exercise.set_logs.filter(completed=False).first()

        if not next_set:
            return Response(
                {"message": "All sets completed!"}, status=status.HTTP_200_OK
            )

        serializer = SetLogSerializer(next_set)
        return Response(serializer.data)


class SetLogViewSet(viewsets.ModelViewSet):
    queryset = SetLog.objects.all()
    serializer_class = SetLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SetLog.objects.filter(session_exercise__session__user=self.request.user)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_set(self, request, pk=None):
        """Mark a set as completed with actual values"""
        set_log = self.get_object()

        if set_log.completed:
            return Response(
                {"error": "Set already completed"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompleteSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update the set with actual values
        set_log.repetitions = serializer.validated_data.get("repetitions")
        set_log.weight_kg = serializer.validated_data.get("weight_kg")
        set_log.duration_seconds = serializer.validated_data.get("duration_seconds")
        set_log.distance_meters = serializer.validated_data.get("distance_meters")
        set_log.rest_seconds = serializer.validated_data.get("rest_seconds", 60)
        set_log.notes = serializer.validated_data.get("notes", "")
        set_log.completed = True
        set_log.completed_at = timezone.now()
        set_log.save()

        # Update completed sets count on session exercise
        session_exercise = set_log.session_exercise
        session_exercise.completed_sets = session_exercise.set_logs.filter(
            completed=True
        ).count()

        # If all sets are complete, mark exercise as completed
        if session_exercise.completed_sets >= session_exercise.planned_sets:
            session_exercise.status = "completed"
            if not session_exercise.completed_at:
                session_exercise.completed_at = timezone.now()

        session_exercise.save()

        response_serializer = SetLogSerializer(set_log)
        return Response(response_serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if Profile.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a profile.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can update only your own profile.")
        serializer.save()


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkoutPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkoutExerciseViewSet(viewsets.ModelViewSet):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]


class WeightLogViewSet(viewsets.ModelViewSet):
    queryset = WeightLog.objects.all()
    serializer_class = WeightLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WeightLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FitnessGoalViewSet(viewsets.ModelViewSet):
    queryset = FitnessGoal.objects.all()
    serializer_class = FitnessGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FitnessGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
