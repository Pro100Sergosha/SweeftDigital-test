# Update apps/workout/admin.py - Add these to existing registrations

from django.contrib import admin
from .models import (
    Profile,
    Exercise,
    WorkoutPlan,
    WorkoutExercise,
    WeightLog,
    FitnessGoal,
    WorkoutSession,
    SessionExercise,
    SetLog,
)


class SetLogInline(admin.TabularInline):
    model = SetLog
    extra = 0
    readonly_fields = ["completed_at"]


class SessionExerciseInline(admin.TabularInline):
    model = SessionExercise
    extra = 0
    readonly_fields = ["started_at", "completed_at"]


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "workout_plan", "status", "started_at", "completed_at"]
    list_filter = ["status", "started_at"]
    search_fields = ["user__username", "workout_plan__title"]
    readonly_fields = ["started_at", "completed_at"]
    inlines = [SessionExerciseInline]


@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display = [
        "workout_exercise",
        "session",
        "status",
        "completed_sets",
        "planned_sets",
    ]
    list_filter = ["status"]
    readonly_fields = ["started_at", "completed_at"]
    inlines = [SetLogInline]


@admin.register(SetLog)
class SetLogAdmin(admin.ModelAdmin):
    list_display = [
        "session_exercise",
        "set_number",
        "completed",
        "repetitions",
        "weight_kg",
    ]
    list_filter = ["completed"]
    readonly_fields = ["completed_at"]


# Keep existing registrations
admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(WorkoutPlan)
admin.site.register(WorkoutExercise)
admin.site.register(WeightLog)
admin.site.register(FitnessGoal)
