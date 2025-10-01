from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Exercise(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    instructions = models.TextField()
    target_muscles = models.CharField(max_length=255)
    equipment = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class WorkoutPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_plans"
    )
    title = models.CharField(max_length=255)
    goal = models.CharField(max_length=255, blank=True, null=True)
    frequency_per_week = models.PositiveIntegerField(default=3)
    session_duration_minutes = models.PositiveIntegerField(default=60)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class WorkoutExercise(models.Model):
    workout_plan = models.ForeignKey(
        WorkoutPlan, on_delete=models.CASCADE, related_name="exercises"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3)
    repetitions = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    distance_meters = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.exercise.name} in {self.workout_plan.name}"


class WeightLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="weight_logs"
    )
    weight = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.weight}kg on {self.date}"


class FitnessGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fitness_goals"
    )
    goal_type = models.CharField(
        max_length=50,
        choices=[
            ("weight", "Weight Objective"),
            ("exercise", "Exercise Achievement"),
        ],
    )
    target_value = models.FloatField()
    description = models.CharField(max_length=255)
    achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Goal: {self.description} ({self.user.username})"
