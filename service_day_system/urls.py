"""
URL configuration for service_day_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from dashboard.gateway import api_gateway

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('ngo_list')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root URL redirects based on auth status
    path('', root_redirect, name='root'),
    # Accounts app handles login, logout, and role-based dashboards
    path('accounts/', include('accounts.urls')),
    # Dashboard app handles NGO activity management
    path('dashboard/', include('dashboard.urls')),
    # Registrations app handles employee activity registration
    path('registrations/', include('registrations.urls')),
    
    # Topic 12: Microservices Gateway (Handling both prefixed and transparent routes)
    path('gateway/<str:service_name>/', api_gateway, name='api_gateway_service_root'),
    path('gateway/<str:service_name>/<path:path>', api_gateway, name='api_gateway'),
    
    # Transparent Forwarding for legacy Browser UI paths
    path('api/activities/', api_gateway, name='legacy_activities'),
    path('users/register/', api_gateway, name='legacy_user_reg'),
    path('api/registrations/', api_gateway, name='legacy_reg'),
    
    # API Documentation (Fixed path)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

handler404 = 'service_day_system.views.error_404_view'
handler500 = 'service_day_system.views.error_500_view'
