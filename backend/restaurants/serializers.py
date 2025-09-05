from rest_framework import serializers
from .models import Restaurant, FoodType, Dish, Menu, Category


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = ["id", "name"]

class CategorySerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Category
        fields = ["id", "name", "restaurant"]

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name", "description"]


class DishSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)
    menus = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), many=True, required=False)
    restaurant = RestaurantSerializer(read_only=True)
    food_type = FoodTypeSerializer(read_only=True)
    food_type = serializers.PrimaryKeyRelatedField(queryset=FoodType.objects.all())

    class Meta:
        model = Dish
        fields = [
            "id", "name", "description", "price", "dish_image",
            "food_type", "categories", "menus",
            "restaurant", "is_available", "created_at",
        ]
        read_only_fields = ["id", "restaurant", "created_at"]

    def validate_food_type(self, value):
        # Enforce only allowed names; shield against accidental rogue entries.
        if value.name not in {"Vegetarian", "Non-Vegetarian"}:
            raise serializers.ValidationError("FoodType must be 'Vegetarian' or 'Non-Vegetarian'.")
        return value
    

    def _validate_related_belongs_to_restaurant(self, restaurant, categories, menus):
        # Categories: either global (restaurant=None) or same restaurant
        invalid_categories = [
            c for c in categories if c.restaurant and c.restaurant_id != restaurant.id
        ]
        if invalid_categories:
            raise serializers.ValidationError("All categories must be global or belong to this restaurant.")
        # Menus: must belong to this restaurant
        invalid_menus = [m for m in menus if m.restaurant_id != restaurant.id]
        if invalid_menus:
            raise serializers.ValidationError("All menus must belong to this restaurant.")
        
    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        menus = validated_data.pop("menus", [])
        user = self.context["request"].user
        restaurant = user.restaurant
        validated_data["restaurant"] = restaurant

        self._validate_related_belongs_to_restaurant(restaurant, categories, menus)

        dish = super().create(validated_data)
        if categories:
            dish.categories.set(categories)
        if menus:
            dish.menus.set(menus)
        return dish


    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        menus = validated_data.pop("menus", None)
        restaurant = instance.restaurant

        if categories is not None or menus is not None:
            self._validate_related_belongs_to_restaurant(restaurant, categories or [], menus or [])

        dish = super().update(instance, validated_data)
        if categories is not None:
            dish.categories.set(categories)
        if menus is not None:
            dish.menus.set(menus)
        return dish
    
# class DishSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Dish
#         fields = ["id", "name", "description", "price", "is_available"]


class MenuSerializer(serializers.ModelSerializer):
    # dishes = DishSerializer(many=True, read_only=True)
    # dish_ids = serializers.PrimaryKeyRelatedField(
    #     queryset=Dish.objects.all(),
    #     many=True,
    #     write_only=True,
    #     source="dishes"
    # )

    class Meta:
        model = Menu
        fields = ["id", "name", "description", "menu_image", "restaurant", "created_at"]
        read_only_fields = ["created_at", "restaurant"]
        
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["restaurant"] = user.restaurant
        return super().create(validated_data)

    def validate(self, attrs):
        # nothing special here—restaurant is set to owner’s restaurant on create
        return attrs