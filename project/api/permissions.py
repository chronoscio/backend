from rest_framework import permissions

class IsStaffOrTargetUser(permissions.BasePermission):
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
        # allow logged in user to view own details, allows staff to view all records
        return request.user.is_staff or obj == request.user
