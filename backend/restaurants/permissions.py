from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsOwnerOfRestaurant(BasePermission):
    """
    Ensures the user is the owner of the restaurant for write operations.
    Assumes viewset sets queryset to the user's restaurant for writes.
    """
    def has_object_permission(self, request, view, obj):
        # obj can be a Dish or Restaurant; both have .restaurant or are Restaurant
        if hasattr(obj, "restaurant"):
            return obj.restaurant.owner == request.user
        return getattr(obj, "owner", None) == request.user
    

class IsOwnerOrReadOnly(BasePermission):
    """
    For Restaurant-scoped objects (Dish, Menu, Category with restaurant).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        rest = getattr(obj, "restaurant", None)
        if rest is None:
            # Global categories cannot be edited by non-admins
            return bool(request.user and request.user.is_superuser)
        return bool(request.user and hasattr(request.user, "restaurant") and request.user.restaurant.id == rest.id)

    def has_permission(self, request, view):
        # For create actions on restaurant-scoped resources: user must own a restaurant
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and hasattr(request.user, "restaurant"))