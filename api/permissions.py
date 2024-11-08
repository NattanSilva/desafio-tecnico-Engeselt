from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS", "POST"]:
            return True
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff
        )


class IsAdminToCreateABook(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff
        )

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        
        if request.method in ["PATCH", "PUT", "DELETE"] and request.user.is_authenticated:
            return request.user.is_superuser or request.user.is_staff
    
        return request.user.is_authenticated