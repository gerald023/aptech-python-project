from rest_framework import serializers
from .models import Restaurant, FoodType, Dish


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = ["id", "name"]

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "description", "menu_card_image"]


class DishSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    food_type = FoodTypeSerializer(read_only=True)
    food_type_id = serializers.PrimaryKeyRelatedField(
        source="food_type", queryset=FoodType.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Dish
        fields = [
            "id", "name", "description", "price", "image",
            "food_type", "food_type_id", "is_available", "restaurant", "created_at"
        ]
        read_only_fields = ["id", "restaurant", "created_at"]