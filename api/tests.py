from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from dashboard.models import NGOActivity
from registrations.models import Registration
from django.utils import timezone
from datetime import timedelta

class APIIntegrationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='employee_joy', password='password123')
        self.activity = NGOActivity.objects.create(
            ngo_name="Integration NGO",
            description="Integration Test",
            location="KL",
            service_type="Food Bank",
            date_time=timezone.now() + timedelta(days=2),
            max_employees=1,
            current_slots_taken=0,
            cut_off_date=timezone.now() + timedelta(days=1),
            is_active=True
        )
        # Use 'v1' as the version for testing
        self.registration_url = reverse('registration-list', kwargs={'version': 'v1'})

    def test_api_registration_workflow(self):
        """Simulate an employee registering for an activity via API."""
        self.client.force_authenticate(user=self.user)
        data = {'activity': self.activity.id}
        
        # Call API
        response = self.client.post(self.registration_url, data, format='json')
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify database
        self.assertEqual(Registration.objects.count(), 1)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.current_slots_taken, 1)

    def test_api_over_registration_prevention(self):
        """Test API blocks registration when max slots reached."""
        self.activity.current_slots_taken = 1
        self.activity.save()
        
        self.client.force_authenticate(user=self.user)
        data = {'activity': self.activity.id}
        
        response = self.client.post(self.registration_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No slots available", str(response.data))
