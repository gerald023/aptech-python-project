from rest_framework import viewsets, mixins, permissions
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsRestaurantOwner
from .models import Dish, Restaurant
from .serializers import DishSerializer

# Create your views here.
class DishViewSet(viewsets.ModelViewSet):
    """
    CRUD for dishes.
    - Owners can list/manage only their restaurant's dishes.
    - Everyone can list/retrieve public dishes (optional; tweak perms as needed).
    """
    serializer_class = DishSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsRestaurantOwner()]

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            # public browsing of dishes across restaurants
            return Dish.objects.select_related("restaurant", "food_type").filter(is_available=True)
        # owner-only: restrict to their own restaurant dishes
        if not hasattr(self.request.user, "restaurant"):
            # Owner doesn't have a restaurant yet
            return Dish.objects.none()
        return Dish.objects.select_related("restaurant", "food_type").filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "restaurant"):
            raise PermissionDenied("You do not have a restaurant.")
        serializer.save(restaurant=user.restaurant)