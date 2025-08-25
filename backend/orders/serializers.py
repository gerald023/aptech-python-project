from rest_framework import serializers
from .models import Order, OrderItem
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
        

class OrderCreateSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
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