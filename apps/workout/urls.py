from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"exercises", ExerciseViewSet)
router.register(r"workout-plans", WorkoutPlanViewSet)
router.register(r"workout-exercises", WorkoutExerciseViewSet)
router.register(r"weight-logs", WeightLogViewSet)
router.register(r"fitness-goals", FitnessGoalViewSet)
router.register(r"workout-sessions", WorkoutSessionViewSet)
router.register(r"session-exercises", SessionExerciseViewSet)
router.register(r"set-logs", SetLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
