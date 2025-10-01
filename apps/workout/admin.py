from django.contrib import admin
from .models import (
    Profile,
    Exercise,
    WorkoutPlan,
    WorkoutExercise,
    WeightLog,
    FitnessGoal,
)


admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(WorkoutPlan)
admin.site.register(WorkoutExercise)
admin.site.register(WeightLog)
admin.site.register(FitnessGoal)
