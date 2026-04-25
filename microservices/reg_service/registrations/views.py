import requests
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Registration
from .serializers import RegistrationSerializer

class RegistrationListCreateView(generics.ListCreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        activity_id = request.data.get('activity_id')
        
        if not user_id or not activity_id:
            return Response({'error': 'user_id and activity_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already registered
        if Registration.objects.filter(user_id=user_id, activity_id=activity_id, status='REGISTERED').exists():
            return Response({'error': 'You are already registered for this activity.'}, status=status.HTTP_400_BAD_REQUEST)

        # Inter-service communication with Basic Circuit Breaker/Error Handling
        NGO_SERVICE_URL = f'http://127.0.0.1:8002/api/activities/{activity_id}/'
        try:
            # 1. Check if slots are available
            check_response = requests.get(f"{NGO_SERVICE_URL}check-slots/", timeout=5)
            
            if check_response.status_code == 404:
                return Response({'error': 'Activity not found in NGO Service.'}, status=status.HTTP_404_NOT_FOUND)
            
            if check_response.status_code != 200:
                return Response({'error': 'Failed to communicate with NGO Service.'}, status=status.HTTP_502_BAD_GATEWAY)

            activity_data = check_response.json()
            if not activity_data.get('has_slot'):
                return Response({'error': 'No remaining slots available.'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Decrement slot in NGO service
            update_response = requests.post(f"{NGO_SERVICE_URL}update-slots/", json={'action': 'register'}, timeout=5)
            if update_response.status_code != 200:
                return Response({'error': 'Failed to reserve slot in NGO Service.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 3. Create Registration
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except requests.exceptions.RequestException as e:
            # Basic circuit breaker / fallback for dependent service offline
            return Response({
                'error': 'Service temporarily unavailable. Could not connect to NGO Service.',
                'details': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class RegistrationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def perform_destroy(self, instance):
        # Update status instead of deleting completely, or just delete and restore slot
        activity_id = instance.activity_id
        NGO_SERVICE_URL = f'http://127.0.0.1:8002/api/activities/{activity_id}/update-slots/'
        
        try:
            # Restore slot
            requests.post(NGO_SERVICE_URL, json={'action': 'cancel'}, timeout=5)
        except requests.exceptions.RequestException:
            pass # Depending on pattern, might queue the event for later reconciliation

        instance.delete()
