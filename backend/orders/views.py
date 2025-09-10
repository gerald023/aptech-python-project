from rest_framework import generics, permissions
from accounts.permissions import IsCustomer, IsRestaurantOwner
from .models import Order, Transaction, Cart, CartItem, OrderItem
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from restaurants.models import Dish
from rest_framework.response import Response
from .serializers import OrderSerializer, OrderCreateSerializer, CartSerializer, TransactionSerializer, AddToCartSerializer, SingleOrderCreateSerializer

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

class SingleOrderCreateView(generics.CreateAPIView):
    serializer_class = SingleOrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order, txn = serializer.save()

        return Response({
            "order": OrderSerializer(order).data,
            "transaction": TransactionSerializer(txn).data
        }, status=status.HTTP_201_CREATED)

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


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        """Get current user's cart"""
        cart = self.get_cart(request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"], url_path="add-item")
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dish = serializer.validated_data["dish"]
        qty = serializer.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, dish=dish, defaults={"quantity": qty, "price": dish.price})

        if not created:
            cart_item.quantity += qty
            cart_item.save()

        return Response(
            {
                "message": "Item added to cart",
                "dish": dish.name,
                "quantity": cart_item.quantity,
                "subtotal": cart_item.subtotal,
            },
            status=status.HTTP_200_OK,
        )
    @action(detail=False, methods=["post"])
    def decrease_item(self, request):
        """Decrease a dish quantity (remove if 0)"""
        dish_id = request.data.get("dish_id")
        qty = int(request.data.get("quantity", 1))

        cart = self.get_cart(request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, dish_id=dish_id)

        if cart_item.quantity > qty:
            cart_item.quantity -= qty
            cart_item.save()
        else:
            cart_item.delete()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Checkout: use OrderCreateSerializer logic, then create Transaction"""
        cart = self.get_cart(request.user)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant = cart.items.first().dish.restaurant

        # Build payload compatible with OrderCreateSerializer
        data = {
            "restaurant_id": restaurant.id,
            "items": [
                {"dish_id": item.dish.id, "quantity": item.quantity}
                for item in cart.items.all()
            ]
        }

        serializer = OrderCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # clear cart
        cart.items.all().delete()

        # create transaction
        txn = Transaction.objects.create(
            order=order,
            user=request.user,
            amount=order.total_amount,
            reference=f"TXN-{order.id.hex[:8]}",
        )

        return Response({
            "order": OrderSerializer(order).data,
            "transaction": TransactionSerializer(txn).data
        }, status=status.HTTP_201_CREATED)
        
