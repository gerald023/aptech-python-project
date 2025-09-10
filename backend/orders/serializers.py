from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem, Transaction
from restaurants.models import Dish

class OrderItemCreateSerializer(serializers.ModelSerializer):
    dish_id = serializers.PrimaryKeyRelatedField(source="dish", queryset=Dish.objects.all())

    class Meta:
        model = OrderItem
        fields = ["dish_id", "quantity"]
        
class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source="dish.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "dish_name", "quantity", "price", "subtotal"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "restaurant", "status", "total_amount", "created_at", "items"]
        read_only_fields = ["status", "total_amount", "created_at", "items"]
        
class SingleOrderCreateSerializer(serializers.Serializer):
    dish_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        try:
            dish = Dish.objects.get(id=data["dish_id"])
        except Dish.DoesNotExist:
            raise serializers.ValidationError("Dish not found.")

        if not dish.is_available:
            raise serializers.ValidationError("This dish is not available.")

        data["dish"] = dish
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        dish = validated_data["dish"]
        quantity = validated_data["quantity"]

        # Create order tied to the dish's restaurant
        order = Order.objects.create(
            customer=user,
            restaurant=dish.restaurant
        )

        # Add the dish as an order item
        OrderItem.objects.create(
            order=order,
            dish=dish,
            quantity=quantity,
            price=dish.price,  # snapshot price
        )

        # recalc total
        order.recalc_total()

        # Create transaction (pending until restaurant owner approves)
        txn = Transaction.objects.create(
            order=order,
            user=user,
            amount=order.total_amount,
            reference=f"TXN-{order.id.hex[:8]}",
        )

        return order, txn

class OrderCreateSerializer(serializers.Serializer):
    restaurant_id = serializers.UUIDField()
    items = OrderItemCreateSerializer(many=True)

    def validate(self, data):
        # ensure all dishes belong to the same restaurant
        from restaurants.models import Restaurant, Dish
        rest_id = data["restaurant_id"]
        dish_ids = [i["dish"].id for i in data["items"]]
        count = Dish.objects.filter(id__in=dish_ids, restaurant_id=rest_id).count()
        if count != len(dish_ids):
            raise serializers.ValidationError("One or more dishes do not belong to the selected restaurant.")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        from restaurants.models import Restaurant
        restaurant = Restaurant.objects.get(id=validated_data["restaurant_id"])
        order = Order.objects.create(customer=user, restaurant=restaurant)
        for item in validated_data["items"]:
            dish = item["dish"]
            qty = item.get("quantity", 1)
            OrderItem.objects.create(order=order, dish=dish, quantity=qty, price=dish.price)
        order.recalc_total()
        return order
    
    

class AddToCartSerializer(serializers.Serializer):
    dish_id = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.all(), source="dish"
    )
    quantity = serializers.IntegerField(min_value=1, default=1)



class CartItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source="dish.name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "dish", "dish_name", "quantity", "price", "subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_amount"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "order", "user", "amount", "reference", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at", "user"]