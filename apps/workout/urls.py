from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    ExerciseViewSet,
    WorkoutPlanViewSet,
    WorkoutExerciseViewSet,
    WeightLogViewSet,
    FitnessGoalViewSet,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"exercises", ExerciseViewSet)
router.register(r"workout-plans", WorkoutPlanViewSet)
router.register(r"workout-exercises", WorkoutExerciseViewSet)
router.register(r"weight-logs", WeightLogViewSet)
router.register(r"fitness-goals", FitnessGoalViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
