from django.conf import settings
from django.db import models


class WorkoutSession(models.Model):
    """Represents an active or completed workout session"""

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_sessions",
    )
    workout_plan = models.ForeignKey(
        "WorkoutPlan", on_delete=models.CASCADE, related_name="sessions"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="in_progress"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    total_duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - {self.workout_plan.title} ({self.status})"


class SessionExercise(models.Model):
    """Tracks each exercise within a workout session"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("skipped", "Skipped"),
    ]

    session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name="session_exercises"
    )
    workout_exercise = models.ForeignKey("WorkoutExercise", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    planned_sets = models.PositiveIntegerField()
    planned_repetitions = models.PositiveIntegerField(null=True, blank=True)
    planned_duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    planned_distance_meters = models.PositiveIntegerField(null=True, blank=True)

    completed_sets = models.PositiveIntegerField(default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.workout_exercise.exercise.name} in {self.session}"


class SetLog(models.Model):
    """Tracks individual sets within an exercise"""

    session_exercise = models.ForeignKey(
        SessionExercise, on_delete=models.CASCADE, related_name="set_logs"
    )
    set_number = models.PositiveIntegerField()

    repetitions = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    distance_meters = models.PositiveIntegerField(null=True, blank=True)

    completed = models.BooleanField(default=False)
    rest_seconds = models.PositiveIntegerField(default=60)
    notes = models.TextField(blank=True, null=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["set_number"]
        unique_together = ["session_exercise", "set_number"]

    def __str__(self):
        return f"Set {self.set_number} of {self.session_exercise}"


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
        return f"{self.title} ({self.user.username})"


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
        return f"{self.exercise.name} in {self.workout_plan.title}"


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
