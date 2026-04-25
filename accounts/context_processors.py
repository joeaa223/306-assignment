from .services.account_service import AccountService
from notifications.models import Notification

def user_roles(request):
    """
    Context processor to add role flags to all templates.
    """
    if request.user.is_authenticated:
        return {
            'is_admin_user': AccountService.is_admin(request.user),
            'is_manager_user': AccountService.is_manager(request.user),
            'is_employee_user': AccountService.is_employee(request.user),
            'user_role_label': AccountService.get_user_role(request.user),
            'recent_notifications': Notification.objects.order_by('-created_at')[:5]
        }
    return {
        'is_admin_user': False,
        'is_manager_user': False,
        'is_employee_user': False,
        'user_role_label': 'Guest'
    }
