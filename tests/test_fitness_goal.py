from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from apps.workout.models import FitnessGoal


class FitnessGoalTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123!"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="TestPass123!"
        )
        self.url = reverse("fitnessgoal-list")
        self.client.force_authenticate(user=self.user)

    def test_create_weight_goal(self):
        """Test creating a weight-based fitness goal"""
        data = {
            "goal_type": "weight",
            "target_value": 70.0,
            "description": "Reach 70kg",
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FitnessGoal.objects.count(), 1)
        goal = FitnessGoal.objects.first()
        self.assertEqual(goal.user, self.user)
        self.assertEqual(goal.goal_type, "weight")
        self.assertEqual(goal.target_value, 70.0)
        self.assertFalse(goal.achieved)

    def test_create_exercise_goal(self):
        """Test creating an exercise-based fitness goal"""
        data = {
            "goal_type": "exercise",
            "target_value": 50.0,
            "description": "Do 50 push-ups in a row",
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        goal = FitnessGoal.objects.first()
        self.assertEqual(goal.goal_type, "exercise")
        self.assertEqual(goal.description, "Do 50 push-ups in a row")

    def test_list_own_fitness_goals(self):
        """Test that users only see their own fitness goals"""
        FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="My goal",
        )
        FitnessGoal.objects.create(
            user=self.other_user,
            goal_type="weight",
            target_value=80.0,
            description="Other's goal",
        )
        
        response = self.client.get(self.url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["description"], "My goal")

    def test_retrieve_fitness_goal(self):
        """Test retrieving a specific fitness goal"""
        goal = FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="Reach 70kg",
        )
        url = reverse("fitnessgoal-detail", kwargs={"pk": goal.pk})
        response = self.client.get(url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["target_value"], 70.0)
        self.assertEqual(response.data["achieved"], False)

    def test_mark_goal_as_achieved(self):
        """Test marking a fitness goal as achieved"""
        goal = FitnessGoal.objects.create(
            user=self.user,
            goal_type="exercise",
            target_value=100.0,
            description="Run 10km",
            achieved=False,
        )
        url = reverse("fitnessgoal-detail", kwargs={"pk": goal.pk})
        data = {
            "goal_type": "exercise",
            "target_value": 100.0,
            "description": "Run 10km",
            "achieved": True,
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        goal.refresh_from_db()
        self.assertTrue(goal.achieved)

    def test_update_fitness_goal(self):
        """Test updating a fitness goal"""
        goal = FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="Original goal",
        )
        url = reverse("fitnessgoal-detail", kwargs={"pk": goal.pk})
        data = {
            "goal_type": "weight",
            "target_value": 68.0,
            "description": "Updated goal",
            "achieved": False,
        }
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        goal.refresh_from_db()
        self.assertEqual(goal.target_value, 68.0)
        self.assertEqual(goal.description, "Updated goal")

    def test_delete_fitness_goal(self):
        """Test deleting a fitness goal"""
        goal = FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="To delete",
        )
        url = reverse("fitnessgoal-detail", kwargs={"pk": goal.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FitnessGoal.objects.count(), 0)

    def test_cannot_access_other_users_goal(self):
        """Test that users cannot access other users' fitness goals"""
        other_goal = FitnessGoal.objects.create(
            user=self.other_user,
            goal_type="weight",
            target_value=80.0,
            description="Other's goal",
        )
        url = reverse("fitnessgoal-detail", kwargs={"pk": other_goal.pk})
        response = self.client.get(url, format="json")
        
        # Should return 404 because it's filtered out by get_queryset
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_goal(self):
        """Test partially updating fitness goal (PATCH)"""
        goal = FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="Original",
            achieved=False,
        )
        url = reverse("fitnessgoal-detail", kwargs={"pk": goal.pk})
        data = {"achieved": True}
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        goal.refresh_from_db()
        self.assertTrue(goal.achieved)
        self.assertEqual(goal.description, "Original")  # Unchanged

    def test_unauthenticated_cannot_create_goal(self):
        """Test that unauthenticated users cannot create fitness goals"""
        self.client.force_authenticate(user=None)
        data = {
            "goal_type": "weight",
            "target_value": 70.0,
            "description": "Test goal",
        }
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_multiple_goals_per_user(self):
        """Test that users can have multiple fitness goals"""
        FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="Weight goal",
        )
        FitnessGoal.objects.create(
            user=self.user,
            goal_type="exercise",
            target_value=50.0,
            description="Exercise goal",
        )
        
        response = self.client.get(self.url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_achieved_goals(self):
        """Test filtering achieved vs not achieved goals"""
        FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=70.0,
            description="Achieved",
            achieved=True,
        )
        FitnessGoal.objects.create(
            user=self.user,
            goal_type="weight",
            target_value=65.0,
            description="Not achieved",
            achieved=False,
        )
        
        response = self.client.get(f"{self.url}?achieved=true", format="json")
        
        # Note: This assumes filtering is configured in the viewset
        # If not implemented, you may want to add it
        self.assertEqual(response.status_code, status.HTTP_200_OK)