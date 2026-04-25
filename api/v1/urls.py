from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import NGOActivityViewSet, RegistrationViewSet, test_view

router = DefaultRouter()
router.register(r'activities', NGOActivityViewSet, basename='activity')
router.register(r'registrations', RegistrationViewSet, basename='registration')

urlpatterns = [
    # API endpoints
    path('test/', test_view),
    path('', include(router.urls)),
]
