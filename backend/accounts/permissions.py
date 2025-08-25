from rest_framework.permissions import BasePermission
from .models import CustomUser

class IsRestaurantOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.RESTAURANT_OWNER)

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.CUSTOMER)
