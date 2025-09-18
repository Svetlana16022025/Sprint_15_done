from rest_framework import permissions


SAFE_METHODS = permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для администратора или только чтение"""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin()))


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение для автора или только чтение"""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator()
                or request.user.is_admin())
