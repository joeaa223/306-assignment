from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .services.registration_service import RegistrationService
from dashboard.models import NGOActivity
from accounts.decorators import employee_required

@employee_required
def register_activity_view(request, activity_id):
    """View to handle employee registration for an activity - Employees Only"""
    if request.method == 'POST':
        success, message = RegistrationService.register_user(request.user, activity_id)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    return redirect('ngo_list')

@employee_required
def withdraw_activity_view(request, activity_id):
    """View to handle employee withdrawal from an activity - Employees Only"""
    if request.method == 'POST':
        success, message = RegistrationService.withdraw_user(request.user, activity_id)
        if success:
            messages.info(request, message)
        else:
            messages.error(request, message)
    return redirect('ngo_list')

@employee_required
def my_registrations_view(request):
    """View to show current user's registered activities - Employees Only"""
    registrations = RegistrationService.get_user_registrations(request.user)
    return render(request, 'registrations/my_schedule.html', {'registrations': registrations})
