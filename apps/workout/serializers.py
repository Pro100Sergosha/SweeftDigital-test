from rest_framework import serializers
from .models import (
    Profile,
    Exercise,
    WorkoutPlan,
    WorkoutExercise,
    WeightLog,
    FitnessGoal,
)


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
