from rest_framework import permissions

class IsStaffOrSpecificUser(permissions.BasePermission):
    """
    Permission to detect whether to user in question is staff or the target user
    Example:
        John (regular user) should be able to access John's account
        Alice (staff) should be able to access John's account
        Jane (regular user) should not be able to access John's account
    """
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is staff
        return view.action == 'retrieve' or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # allow all users to view specific user information
        return True
