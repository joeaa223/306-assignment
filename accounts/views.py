from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .services.account_service import AccountService


def login_view(request):
    """
    Login view following BIT306 Lab 6 standards.
    - Only handles POST parameter extraction and delegates to AccountService.
    - Implements role-based redirection after successful login.
    - Handles the 'next' URL parameter for protected page redirects.
    """
    # If user is already logged in, redirect to their dashboard
    if request.user.is_authenticated:
        redirect_url = AccountService.get_redirect_url_for_user(request.user)
        return redirect(redirect_url)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Delegate authentication to the Service Layer
        success, result = AccountService.authenticate_user(request, username, password)

        if success:
            user = result
            messages.success(request, f'Welcome back, {user.username}!')

            # --- Topic 9.1: Role-Specific Session Preferences ---
            if AccountService.is_admin(user) or AccountService.is_manager(user):
                request.session['role_theme'] = 'admin-dark'
                request.session['management_mode'] = True
            else:
                request.session['role_theme'] = 'employee-light'
                request.session['last_viewed_ngo'] = 'None'

            # Check for 'next' URL parameter first
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)

            # Role-based redirection via Service Layer
            redirect_url = AccountService.get_redirect_url_for_user(user)
            return redirect(redirect_url)
        else:
            # result is the error message string
            messages.error(request, result)

    # GET request or failed login — render the login form
    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
    """
    Custom logout view that supports GET requests (Django 5.x compatibility).
    Delegates to AccountService for actual logout logic.
    """
    AccountService.logout_user(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def admin_dashboard_view(request):
    """
    Admin/Manager Dashboard — redirects to the main NGO activity list.
    Access restricted to Admin and Manager groups.
    """
    if not (AccountService.is_admin(request.user) or AccountService.is_manager(request.user)):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('employee_dashboard')
    return redirect('ngo_list')


@login_required
def employee_dashboard_view(request):
    """
    Employee Dashboard — redirects to the main NGO activity list.
    All authenticated employees can access this.
    """
    return redirect('ngo_list')
