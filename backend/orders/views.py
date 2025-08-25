from rest_framework import generics, permissions
from accounts.permissions import IsCustomer, IsRestaurantOwner
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by("-created_at")

class RestaurantOrdersView(generics.ListAPIView):
    """
    For restaurant owners to view/filter today's orders or by status, etc.
    Add filtering with query params like ?status=pending
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        qs = Order.objects.filter(restaurant=self.request.user.restaurant).order_by("-created_at")
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs
