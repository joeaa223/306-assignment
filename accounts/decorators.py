from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from .services.account_service import AccountService

def admin_required(view_func):
    """
    Decorator for views that checks if the user is an Admin or Manager.
    Redirects to ngo_list with an error message if not authorized.
    """
    def check_role(user):
        if not user.is_authenticated:
            return False
        return AccountService.is_admin(user) or AccountService.is_manager(user)
    
    actual_decorator = user_passes_test(
        check_role,
        login_url='login',
        redirect_field_name=None
    )
    
    # We wrap the view to add a message if the check fails
    def wrapper(request, *args, **kwargs):
        if not check_role(request.user):
            messages.error(request, 'Access denied. Admin or Manager privileges required.')
            return redirect('ngo_list')
        return view_func(request, *args, **kwargs)
    
    return wrapper

def employee_required(view_func):
    """
    Decorator for views that checks if the user is an Employee.
    Admins and Managers are NOT allowed to access these views if strict isolation is required.
    """
    def check_role(user):
        if not user.is_authenticated:
            return False
        return AccountService.is_employee(user)
    
    def wrapper(request, *args, **kwargs):
        if not check_role(request.user):
            messages.error(request, 'Access denied. Only Employees can perform this action.')
            return redirect('ngo_list')
        return view_func(request, *args, **kwargs)
    
    return wrapper
