from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from dashboard.models import NGOActivity
from registrations.models import Registration
from registrations.services.registration_service import RegistrationService
from .serializers import NGOActivitySerializer, RegistrationSerializer

print("DEBUG: API Views Loaded")

class NGOActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for NGO Management (Admin) and Activity Listing (Employee).
    """
    queryset = NGOActivity.objects.all().order_by('-date_time')
    serializer_class = NGOActivitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['location', 'service_type', 'is_active']
    search_fields = ['ngo_name', 'description']

    def get_permissions(self):
        """
        Only Admin/Manager can create, update, delete.
        Employees can only list and retrieve.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'toggle']:
            # For simplicity in this demo, checking is_staff. 
            # In production, check group membership.
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle activity status"""
        activity = self.get_object()
        activity.is_active = not activity.is_active
        activity.save()
        return Response({'status': 'active' if activity.is_active else 'inactive'})

class RegistrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Activity Registration and Cancellation (Employee).
    """
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own registrations
        return Registration.objects.filter(user=self.request.user, status='REGISTERED')

    def create(self, request, *args, **kwargs):
        """Register for an activity using RegistrationService"""
        activity_id = request.data.get('activity')
        if not activity_id:
            return Response({'error': 'activity ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # We call the service to ensure logic consistency and transaction safety
        success, message = RegistrationService.register_user(request.user, activity_id)
        
        if success:
            registration = Registration.objects.get(user=request.user, activity_id=activity_id, status='REGISTERED')
            serializer = self.get_serializer(registration)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='withdraw/(?P<activity_id>[0-9]+)')
    def withdraw(self, request, activity_id=None):
        """Cancel/Withdraw from an activity using RegistrationService"""
        success, message = RegistrationService.withdraw_user(request.user, activity_id)
        
        if success:
            return Response({'detail': message}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view
@api_view(['GET'])
def test_view(request, version):
    return Response({"message": "test"})
