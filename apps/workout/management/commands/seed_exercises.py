from django.core.management.base import BaseCommand
from apps.workout.models import Exercise


class Command(BaseCommand):
    help = "Seed database with predefined exercises"

    def handle(self, *args, **kwargs):
        exercises = [
            {
                "name": "Push Ups",
                "description": "A basic bodyweight exercise for chest and triceps.",
                "instructions": "Keep your body straight, lower until elbows are 90°, then push up.",
                "target_muscles": "chest, triceps, shoulders",
                "equipment": "bodyweight",
            },
            {
                "name": "Pull Ups",
                "description": "Upper body exercise focusing on back and biceps.",
                "instructions": "Grip bar shoulder-width, pull chin above bar, lower slowly.",
                "target_muscles": "back, biceps",
                "equipment": "pull-up bar",
            },
            {
                "name": "Squats",
                "description": "Compound leg exercise.",
                "instructions": "Feet shoulder-width apart, squat until thighs parallel, return up.",
                "target_muscles": "quadriceps, glutes, hamstrings",
                "equipment": "bodyweight or barbell",
            },
            {
                "name": "Deadlift",
                "description": "Full-body strength exercise.",
                "instructions": "Bend at hips, lift barbell keeping back straight, stand tall.",
                "target_muscles": "back, glutes, hamstrings",
                "equipment": "barbell",
            },
            {
                "name": "Bench Press",
                "description": "Chest strength exercise with barbell.",
                "instructions": "Lower bar to chest, push back up until arms extended.",
                "target_muscles": "chest, triceps, shoulders",
                "equipment": "barbell, bench",
            },
            {
                "name": "Overhead Press",
                "description": "Shoulder pressing movement.",
                "instructions": "Lift barbell overhead until arms straight, lower slowly.",
                "target_muscles": "shoulders, triceps",
                "equipment": "barbell, dumbbells",
            },
            {
                "name": "Plank",
                "description": "Isometric core strength exercise.",
                "instructions": "Hold body straight, resting on forearms and toes.",
                "target_muscles": "core, abs",
                "equipment": "bodyweight",
            },
            {
                "name": "Lunges",
                "description": "Leg strength exercise with single-leg focus.",
                "instructions": "Step forward, bend knees to 90°, push back up.",
                "target_muscles": "quadriceps, glutes, hamstrings",
                "equipment": "bodyweight, dumbbells",
            },
            {
                "name": "Bicep Curls",
                "description": "Isolation exercise for arms.",
                "instructions": "Curl dumbbells upward while keeping elbows fixed.",
                "target_muscles": "biceps",
                "equipment": "dumbbells, barbell",
            },
            {
                "name": "Tricep Dips",
                "description": "Bodyweight exercise for triceps.",
                "instructions": "Lower body by bending elbows, push back up.",
                "target_muscles": "triceps",
                "equipment": "parallel bars, bench",
            },
            {
                "name": "Mountain Climbers",
                "description": "Cardio and core exercise.",
                "instructions": "In push-up position, alternate bringing knees to chest quickly.",
                "target_muscles": "core, shoulders, legs",
                "equipment": "bodyweight",
            },
            {
                "name": "Burpees",
                "description": "Full-body explosive exercise.",
                "instructions": "Squat down, kick legs back, do a push-up, jump up explosively.",
                "target_muscles": "full body",
                "equipment": "bodyweight",
            },
            {
                "name": "Russian Twists",
                "description": "Core rotation exercise.",
                "instructions": "Sit with knees bent, lean back, twist torso side to side.",
                "target_muscles": "obliques, abs",
                "equipment": "bodyweight, medicine ball",
            },
            {
                "name": "Leg Press",
                "description": "Machine-based leg strength exercise.",
                "instructions": "Push weight platform with legs, extend fully, control back down.",
                "target_muscles": "quadriceps, glutes",
                "equipment": "leg press machine",
            },
            {
                "name": "Calf Raises",
                "description": "Isolation exercise for calves.",
                "instructions": "Stand on toes, lift heels, lower slowly.",
                "target_muscles": "calves",
                "equipment": "bodyweight, dumbbells",
            },
            {
                "name": "Bicycle Crunches",
                "description": "Dynamic core exercise.",
                "instructions": "Alternate elbow to opposite knee while cycling legs.",
                "target_muscles": "abs, obliques",
                "equipment": "bodyweight",
            },
            {
                "name": "Jumping Jacks",
                "description": "Cardio warm-up exercise.",
                "instructions": "Jump with legs apart while raising arms overhead, return to start.",
                "target_muscles": "full body, cardio",
                "equipment": "bodyweight",
            },
            {
                "name": "Kettlebell Swings",
                "description": "Explosive power exercise.",
                "instructions": "Swing kettlebell from between legs to shoulder height using hips.",
                "target_muscles": "glutes, hamstrings, shoulders",
                "equipment": "kettlebell",
            },
            {
                "name": "Rowing Machine",
                "description": "Cardio and back exercise.",
                "instructions": "Push legs, pull handle to chest, return smoothly.",
                "target_muscles": "back, biceps, legs, cardio",
                "equipment": "rowing machine",
            },
            {
                "name": "Side Plank",
                "description": "Isometric core exercise.",
                "instructions": "Hold body on side supported by forearm, keep straight line.",
                "target_muscles": "obliques, core",
                "equipment": "bodyweight",
            },
        ]

        for ex in exercises:
            Exercise.objects.get_or_create(name=ex["name"], defaults=ex)

        self.stdout.write(self.style.SUCCESS("Successfully seeded 20 exercises"))
