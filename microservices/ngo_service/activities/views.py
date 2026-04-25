from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import NGOActivity
from .serializers import ActivitySerializer

class ActivityListCreateView(generics.ListCreateAPIView):
    queryset = NGOActivity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [AllowAny]

class CheckSlotView(APIView):
    permission_classes = [AllowAny]
    """
    Internal Microservice API used by Registration Service.
    Verifies if an activity exists and if there are slots available.
    """
    def get(self, request, pk):
        activity = get_object_or_404(NGOActivity, pk=pk)
        if not activity.is_active:
            return Response({'error': 'Activity is not active.'}, status=status.HTTP_400_BAD_REQUEST)
        
        has_slot = activity.remaining_slots > 0
        return Response({
            'activity_id': activity.id,
            'ngo_name': activity.ngo_name,
            'has_slot': has_slot,
            'remaining_slots': activity.remaining_slots,
            'max_employees': activity.max_employees
        })

class DecrementSlotView(APIView):
    """
    Internal Microservice API used by Registration Service.
    Decrements a slot when a user registers. Allows negative for cancellation.
    """
    def post(self, request, pk):
        activity = get_object_or_404(NGOActivity, pk=pk)
        action = request.data.get('action', 'register') # register or cancel

        if action == 'register':
            if activity.remaining_slots <= 0:
                return Response({'error': 'No slots available.'}, status=status.HTTP_400_BAD_REQUEST)
            activity.current_slots_taken += 1
        elif action == 'cancel':
            activity.current_slots_taken = max(0, activity.current_slots_taken - 1)
            
        activity.save()
        return Response({'success': True, 'remaining_slots': activity.remaining_slots})
