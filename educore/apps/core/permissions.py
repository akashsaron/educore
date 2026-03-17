"""
apps/core/permissions.py

Role-based permission classes for EduCore ERP.
Usage:
    from apps.core.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher

    class MyView(APIView):
        permission_classes = [IsAuthenticated, IsAdmin]
"""
from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class IsAdmin(BasePermission):
    """Allows super_admin and admin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('super_admin', 'admin')


class IsPrincipal(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('super_admin', 'admin', 'principal')


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsAdminOrTeacher(BasePermission):
    """Admin full access; teachers read-only."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role in ('super_admin', 'admin', 'principal'):
            return True
        if request.user.role == 'teacher':
            return request.method in ('GET', 'HEAD', 'OPTIONS')
        return False


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('super_admin', 'admin', 'accountant')


class IsLibrarian(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('super_admin', 'admin', 'librarian')


class IsStaff(BasePermission):
    """Any staff role (not student/parent)."""
    STAFF_ROLES = ('super_admin', 'admin', 'principal', 'teacher', 'accountant', 'librarian')

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.STAFF_ROLES


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner (student/parent) or admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ('super_admin', 'admin', 'principal'):
            return True
        # Students can only access their own record
        if hasattr(obj, 'student') and hasattr(request.user, 'student_profile'):
            return obj.student == request.user.student_profile
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in ('GET', 'HEAD', 'OPTIONS')
