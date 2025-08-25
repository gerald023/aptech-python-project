from rest_framework.permissions import BasePermission

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