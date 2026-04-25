from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .forms import NGOActivityForm
from .services.activity_service import ActivityService
from .models import NGOActivity
from registrations.services.registration_service import RegistrationService
from accounts.decorators import admin_required
from accounts.services.account_service import AccountService
from notifications.models import Notification

@cache_page(60 * 15)  # Cache for 15 minutes (Topic 9.2a)
@vary_on_cookie        # CRITICAL: Ensures cache is per-user so admin data doesn't leak
@login_required
def ngo_list_view(request):
    """View to list all NGO activities"""
    if AccountService.is_admin(request.user) or AccountService.is_manager(request.user):
        activities = ActivityService.get_all_activities()
    else:
        activities = ActivityService.get_available_activities()
    
    # Get IDs of activities the user is registered for
    registered_ids = []
    if not (AccountService.is_admin(request.user) or AccountService.is_manager(request.user)):
        registered_ids = [r.activity_id for r in RegistrationService.get_user_registrations(request.user)]

    return render(request, 'dashboard/ngo_list.html', {
        'activities': activities,
        'registered_ids': registered_ids
    })

@login_required
def activity_detail_view(request, pk):
    """View to show detailed information about an NGO activity"""
    activity = get_object_or_404(NGOActivity, pk=pk)
    return render(request, 'dashboard/activity_detail.html', {'activity': activity})

@admin_required
def create_activity_view(request):
    """View to create a new activity - Admin Only"""
    if request.method == 'POST':
        form = NGOActivityForm(request.POST)
        if form.is_valid():
            ActivityService.create_activity(form.cleaned_data)
            messages.success(request, 'Activity created successfully!')
            return redirect('ngo_list')
    else:
        form = NGOActivityForm()
    return render(request, 'dashboard/ngo_form.html', {'form': form, 'title': 'Create New Activity'})

@admin_required
def update_activity_view(request, pk):
    """View to update an existing activity - Admin Only"""
    activity = get_object_or_404(NGOActivity, pk=pk)
    if request.method == 'POST':
        form = NGOActivityForm(request.POST, instance=activity)
        if form.is_valid():
            ActivityService.update_activity(pk, form.cleaned_data)
            messages.success(request, 'Activity updated successfully!')
            return redirect('ngo_list')
    else:
        form = NGOActivityForm(instance=activity)
    return render(request, 'dashboard/ngo_form.html', {'form': form, 'title': 'Update Activity Details'})

@admin_required
def toggle_activity_status_view(request, pk):
    """View to toggle activity active/inactive status - Admin Only"""
    ActivityService.toggle_activity_status(pk)
    messages.info(request, 'Activity status updated')
    return redirect('ngo_list')

@admin_required
def delete_activity_view(request, pk):
    """View to permanently delete an activity - Admin Only"""
    ActivityService.delete_activity(pk)
    messages.warning(request, 'Activity permanently removed.')
    return redirect('ngo_list')

@admin_required
def notifications_view(request):
    """View to manage notifications and reminders - Admin Only"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            # Topic 11.3: Creating this object triggers the post_save signal
            # which broadcasts the message via WebSockets.
            Notification.objects.create(title=title, content=content)
            messages.success(request, f'Broadcast message "{title}" has been sent to all employees!')
            return redirect('admin_notifications')
            
    return render(request, 'dashboard/notifications.html')

@login_required
def notification_history_view(request):
    """View to show all historical notifications for the user"""
    # Fetch all notifications, newest first
    notifications = Notification.objects.order_by('-created_at')
    return render(request, 'dashboard/notification_history.html', {'notifications': notifications})

def accounts_info_view(request):
    """Public view to show test credentials for project demonstration"""
    return render(request, 'dashboard/accounts_info.html')

@admin_required
def monitoring_view(request):
    """
    View for Administrators to monitor employee participation.
    Use Case 4: Monitor Employee Participation and Slot Utilisation.
    """
    # Get overall stats using the Service Layer
    overall_stats = RegistrationService.get_overall_stats()
    
    # Get all activities and their participants
    activities = ActivityService.get_all_activities()
    
    activity_data = []
    for activity in activities:
        participants = RegistrationService.get_activity_participants(activity.id)
        activity_data.append({
            'activity': activity,
            'participants': participants,
            'participant_count': len(participants),
            'utilization': round((activity.current_slots_taken / activity.max_employees) * 100) if activity.max_employees > 0 else 0
        })

    context = {
        'overall_stats': overall_stats,
        'activity_data': activity_data
    }
    return render(request, 'dashboard/monitoring.html', context)

@admin_required
def qr_generator_view(request, pk):
    """
    Mock view for Admin to 'generate' a QR code.
    Use Case 6: Employee Check-In via QR Code.
    """
    activity = ActivityService.get_activity(pk)
    return render(request, 'dashboard/qr_generator.html', {'activity': activity})

@login_required
def virtual_scanner_view(request, pk):
    """
    Mock view to show a 'scannning' animation before success.
    Use Case 6: Employee Check-In via QR Code.
    """
    activity = ActivityService.get_activity(pk)
    return render(request, 'dashboard/virtual_scanner.html', {'activity': activity})

