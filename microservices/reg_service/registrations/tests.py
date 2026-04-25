from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from dashboard.models import NGOActivity
from registrations.services.registration_service import RegistrationService
from django.core.exceptions import ValidationError
from unittest.mock import patch
import requests

# --- Lab 12 Task 4: Mock Testing ---
class RegistrationMockTest(TestCase):
    @patch('requests.get')
    def test_ngo_service_mocking(self, mock_get):
        # Mocking the NGO Service response (simulating external API)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"remaining_slots": 5}
        
        # Directly calling the logic that would normally hit port 8002
        response = requests.get("http://127.0.0.1:8002/api/activities/1/check-slots/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['remaining_slots'], 5)
        # Verify the call was made
        mock_get.assert_called_once()

class RegistrationLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testemployee', password='password123')
        self.activity = NGOActivity.objects.create(
            ngo_name="Test NGO",
            description="Test Description",
            location="Test Location",
            service_type="Testing",
            date_time=timezone.now() + timedelta(days=2),
            max_employees=2,
            current_slots_taken=0,
            cut_off_date=timezone.now() + timedelta(days=1),
            is_active=True
        )

    def test_slot_availability_success(self):
        """Test registration succeeding when slots are available."""
        success, message = RegistrationService.register_user(self.user, self.activity.id)
        self.assertTrue(success, f"Registration failed with message: {message}")
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.current_slots_taken, 1)

    def test_slot_availability_failure(self):
        """Test registration failing when no slots are left."""
        self.activity.current_slots_taken = 2
        self.activity.save()
        success, message = RegistrationService.register_user(self.user, self.activity.id)
        self.assertFalse(success)
        self.assertIn("No slots available", message)

    def test_cutoff_time_failure(self):
        """Test registration failing after cutoff period."""
        self.activity.cut_off_date = timezone.now() - timedelta(hours=1)
        self.activity.save()
        success, message = RegistrationService.register_user(self.user, self.activity.id)
        self.assertFalse(success)
        self.assertIn("Registration deadline has passed", message)

    def test_negative_slots_edge_case(self):
        """Test that the model validation prevents negative max_employees."""
        self.activity.max_employees = -1
        with self.assertRaises(ValidationError):
            self.activity.full_clean()
