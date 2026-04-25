from rest_framework import serializers
from django.utils import timezone
from dashboard.models import NGOActivity
from registrations.models import Registration
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class NGOActivitySerializer(serializers.ModelSerializer):
    remaining_slots = serializers.ReadOnlyField()

    class Meta:
        model = NGOActivity
        fields = [
            'id', 'ngo_name', 'description', 'location', 
            'service_type', 'date_time', 'max_employees', 
            'current_slots_taken', 'remaining_slots', 
            'cut_off_date', 'is_active'
        ]

class RegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    activity_details = NGOActivitySerializer(source='activity', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'activity', 'activity_details', 'registered_at', 'status']
        read_only_fields = ['registered_at', 'status']

    def validate(self, data):
        """
        Check if the activity has available slots and current time is before cut-off.
        Note: This is also handled in the RegistrationService, but we implement it here
        as per Topic 8 requirements.
        """
        activity = data.get('activity')
        
        if not activity.is_active:
            raise serializers.ValidationError("This activity is not active.")

        if timezone.now() > activity.cut_off_date:
            raise serializers.ValidationError("Registration deadline has passed.")

        if activity.current_slots_taken >= activity.max_employees:
            raise serializers.ValidationError("No slots available. This activity is full.")

        # Check if user already registered (for the current user, handled in perform_create)
        return data
