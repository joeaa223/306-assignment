from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import NGOActivity

# --- Lab 12 Task 2: Unit Testing (Model Test) ---
class NGOActivityModelTest(TestCase):
    def test_activity_creation(self):
        activity = NGOActivity.objects.create(
            ngo_name="Test NGO",
            activity_name="Unit Test Activity",
            max_employees=5,
            location="Test Loc",
            service_type="Test Type",
            description="Test Desc"
        )
        self.assertEqual(activity.activity_name, "Unit Test Activity")
        # Check if the calculated property remaining_slots works
        self.assertEqual(activity.remaining_slots, 5)

# --- Lab 12 Task 3: Integration & API Testing ---
class NGOActivityAPITest(APITestCase):
    def setUp(self):
        self.activity = NGOActivity.objects.create(
            ngo_name="Initial NGO",
            activity_name="Initial Activity",
            max_employees=10,
            location="KL",
            description="Test description",
            service_type="Health"
        )
        # Assuming the URL name in ngo_service/activities/urls.py is 'activity-list-create'
        self.list_url = '/api/activities/' 

    def test_get_activities_list(self):
        # Integration test (View + Model + Data)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_create_activity_api(self):
        # API test (JSON post and verification)
        data = {
            "ngo_name": "New NGO",
            "activity_name": "New Activity",
            "max_employees": 20,
            "location": "PJ",
            "description": "API Test",
            "service_type": "Social"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NGOActivity.objects.count(), 2)
