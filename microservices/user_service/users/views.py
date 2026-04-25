from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import CustomUser
from .serializers import UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

class UserProfileView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
