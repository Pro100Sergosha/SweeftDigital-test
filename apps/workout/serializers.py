from rest_framework import serializers
from .models import *


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "user", "weight", "height", "created_at"]
        read_only_fields = ["id", "created_at", "user"]


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "description",
            "instructions",
            "target_muscles",
            "equipment",
        ]


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(), source="exercise", write_only=True
    )

    class Meta:
        model = WorkoutExercise
        fields = [
            "id",
            "workout_plan",
            "exercise",
            "exercise_id",
            "sets",
            "repetitions",
            "duration_seconds",
            "distance_meters",
        ]


class WorkoutPlanSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = [
            "id",
            "user",
            "title",
            "goal",
            "frequency_per_week",
            "session_duration_minutes",
            "created_at",
            "exercises",
        ]
        read_only_fields = ["id", "created_at", "user"]


class WeightLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightLog
        fields = ["id", "user", "weight", "date"]
        read_only_fields = ["id", "date", "user"]


class FitnessGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessGoal
        fields = [
            "id",
            "user",
            "goal_type",
            "target_value",
            "description",
            "achieved",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]


class SetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetLog
        fields = [
            "id",
            "session_exercise",
            "set_number",
            "repetitions",
            "weight_kg",
            "duration_seconds",
            "distance_meters",
            "completed",
            "rest_seconds",
            "notes",
            "completed_at",
        ]
        read_only_fields = ["id", "completed_at"]


class SessionExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(
        source="workout_exercise.exercise.name", read_only=True
    )
    exercise_description = serializers.CharField(
        source="workout_exercise.exercise.description", read_only=True
    )
    exercise_instructions = serializers.CharField(
        source="workout_exercise.exercise.instructions", read_only=True
    )
    set_logs = SetLogSerializer(many=True, read_only=True)

    class Meta:
        model = SessionExercise
        fields = [
            "id",
            "session",
            "workout_exercise",
            "exercise_name",
            "exercise_description",
            "exercise_instructions",
            "order",
            "status",
            "planned_sets",
            "planned_repetitions",
            "planned_duration_seconds",
            "planned_distance_meters",
            "completed_sets",
            "started_at",
            "completed_at",
            "notes",
            "set_logs",
        ]
        read_only_fields = ["id", "started_at", "completed_at"]


class SessionExerciseDetailSerializer(SessionExerciseSerializer):
    """Detailed serializer with full exercise information"""

    exercise = ExerciseSerializer(source="workout_exercise.exercise", read_only=True)

    class Meta(SessionExerciseSerializer.Meta):
        fields = SessionExerciseSerializer.Meta.fields + ["exercise"]


class WorkoutSessionSerializer(serializers.ModelSerializer):
    workout_plan_title = serializers.CharField(
        source="workout_plan.title", read_only=True
    )
    session_exercises = SessionExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutSession
        fields = [
            "id",
            "user",
            "workout_plan",
            "workout_plan_title",
            "status",
            "started_at",
            "completed_at",
            "notes",
            "total_duration_minutes",
            "session_exercises",
        ]
        read_only_fields = ["id", "user", "started_at", "completed_at"]


class StartWorkoutSessionSerializer(serializers.Serializer):
    """Serializer for starting a new workout session"""

    workout_plan_id = serializers.IntegerField()

    def validate_workout_plan_id(self, value):
        user = self.context["request"].user

        try:
            workout_plan = WorkoutPlan.objects.get(id=value, user=user)
        except WorkoutPlan.DoesNotExist:
            raise serializers.ValidationError(
                "Workout plan not found or you don't have access."
            )

        # Check if there's already an active session
        active_session = WorkoutSession.objects.filter(
            user=user, status="in_progress"
        ).exists()

        if active_session:
            raise serializers.ValidationError(
                "You already have an active workout session."
            )

        return value


class CompleteSessionSerializer(serializers.Serializer):
    """Serializer for completing a workout session"""

    notes = serializers.CharField(required=False, allow_blank=True)


class UpdateSessionExerciseSerializer(serializers.Serializer):
    """Serializer for updating session exercise status"""

    status = serializers.ChoiceField(
        choices=["pending", "in_progress", "completed", "skipped"]
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class CompleteSetSerializer(serializers.Serializer):
    """Serializer for completing a set"""

    repetitions = serializers.IntegerField(required=False, allow_null=True)
    weight_kg = serializers.FloatField(required=False, allow_null=True)
    duration_seconds = serializers.IntegerField(required=False, allow_null=True)
    distance_meters = serializers.IntegerField(required=False, allow_null=True)
    rest_seconds = serializers.IntegerField(default=60)
    notes = serializers.CharField(required=False, allow_blank=True)
