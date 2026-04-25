from django.contrib.auth import authenticate, login, logout


class AccountService:
    """
    Service Layer for authentication and role-based access control (RBAC).
    Encapsulates all authentication logic away from the View layer,
    following the BIT306 'Fat Service, Skinny View' principle.
    """

    # --- Authentication ---

    @staticmethod
    def authenticate_user(request, username, password):
        """
        Authenticates a user using Django's built-in authenticate() and login().
        Returns (success: bool, user_or_error: User | str).
        """
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return True, user
        else:
            return False, "Invalid username or password."

    @staticmethod
    def logout_user(request):
        """Logs out the current user."""
        logout(request)

    # --- Role Checking (RBAC via Django Groups) ---

    @staticmethod
    def is_admin(user):
        """Check if the user is a superuser OR belongs to the 'Admin' group."""
        return user.is_superuser or user.groups.filter(name='Admin').exists()

    @staticmethod
    def is_manager(user):
        """Check if the user is a superuser OR belongs to the 'Manager' group."""
        return user.is_superuser or user.groups.filter(name='Manager').exists()

    @staticmethod
    def is_employee(user):
        """Check if the user belongs to the 'Employee' group."""
        return user.groups.filter(name='Employee').exists()

    @staticmethod
    def get_user_role(user):
        """
        Determines the primary role of the user based on group membership.
        Returns role string for display purposes.
        Priority: Admin > Manager > Employee.
        """
        if AccountService.is_admin(user):
            return 'Admin'
        elif AccountService.is_manager(user):
            return 'Manager'
        elif AccountService.is_employee(user):
            return 'Employee'
        return 'Unknown'

    @staticmethod
    def get_redirect_url_for_user(user):
        """
        Determines the correct dashboard URL based on the user's role.
        This implements the role-based redirection logic required by Lab 6.
        """
        if AccountService.is_admin(user):
            return 'admin_dashboard'
        elif AccountService.is_manager(user):
            return 'admin_dashboard'  # Managers share admin dashboard
        elif AccountService.is_employee(user):
            return 'employee_dashboard'
        return 'login'  # Fallback
