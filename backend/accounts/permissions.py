from rest_framework.permissions import BasePermission


def role_permission(*roles):
    """Build a permission class that allows only the given roles."""
    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user.is_authenticated and request.user.role in roles)
    return RolePermission


IsAdmin = role_permission("admin")
IsStaffOrAdmin = role_permission("staff", "admin")
IsCustomer = role_permission("customer")
IsCustomerOrAdmin = role_permission("customer", "admin")
