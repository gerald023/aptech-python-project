from rest_framework import serializers
from .models import Restaurant, FoodType, Dish, Menu, Category
import cloudinary.uploader


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
    restaurant_image_upload = serializers.ImageField(write_only=True, required=False)
    class Meta:
        model = Restaurant
        fields = ["id", "name", "description", 'restaurant_image', 'restaurant_image_upload', 'owner']
        read_only_fields=['id', 'name', 'owner', 'description', 'restaurant_image']
        
    def create(self, validated_data):
        restaurant_image_upload = validated_data.pop("restaurant_image_upload", None)
        owner = validated_data.pop("owner")
        restaurant = Restaurant.objects.create(user=owner, **validated_data)
        
        if restaurant_image_upload:
            upload = cloudinary.uploader.upload(
                restaurant_image_upload,
                folder="aptech_python_onlineFood_delivery/restaurant_image"
            )
            restaurant.restaurant_image = upload.get('secure_url')
            restaurant.save()
        return restaurant;
    
    def update(self, instance, validated_data):
        restaurant_image_upload = validated_data.pop("restaurant_image_upload", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if restaurant_image_upload:
            upload = cloudinary.uploader.upload(
                restaurant_image_upload,
                folder="aptech_python_onlineFood_delivery/restaurant_image"
            )
            instance.restaurant_image = upload.get("secure_url")
        instance.save()
        return instance
        


class DishSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)
    menus = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), many=True, required=False)
    restaurant = RestaurantSerializer(read_only=True)
    food_type = FoodTypeSerializer(read_only=True)
    food_type = serializers.PrimaryKeyRelatedField(queryset=FoodType.objects.all())
    dish_image_upload = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Dish
        fields = [
            "id", "name", "description", "price", "dish_image",
            "food_type", "categories", "menus",
            "restaurant", "is_available", "created_at", "dish_image_upload"
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
        dish_image_upload = validated_data.pop("dish_image_upload", None)
        user = self.context["request"].user
        restaurant = user.restaurant
        
        validated_data["restaurant"] = restaurant
        
        dish = Dish.objects.create(**validated_data)
        
        if dish_image_upload:
            upload = cloudinary.uploader.upload(
                dish_image_upload,
                folder="aptech_python_onlineFood_delivery/dishes"
            )
            dish.dish_image = upload.get('secure_url')
            dish.save()

        self._validate_related_belongs_to_restaurant(restaurant, categories, menus)

        if categories:
            dish.categories.set(categories)
        if menus:
            dish.menus.set(menus)
        return dish


    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        menus = validated_data.pop("menus", None)
        # restaurant = instance.restaurant
        dish_image_upload = validated_data.pop("dish_image_upload", None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if dish_image_upload:
            upload = cloudinary.uploader.upload(
                dish_image_upload,
                folder = "aptech_python_onlineFood_delivery/dishes"
            )
            instance.dish_image = upload.get("secure_url")
            
            instance.save()
            return instance
        if categories is not None or menus is not None:
            self._validate_related_belongs_to_restaurant(instance.restaurant, categories or [], menus or [])

        if categories is not None:
            instance.categories.set(categories)
        if menus is not None:
            instance.menus.set(menus)
        return instance
    


class MenuSerializer(serializers.ModelSerializer):
    menu_image_upload = serializers.ImageField(write_only=True, required=False)
    class Meta:
        model = Menu
        fields = ["id", "name", "description", "menu_image", "restaurant", "created_at", "menu_image_upload"]
        read_only_fields = ["created_at", "restaurant", "menu_image"]
        
    def create(self, validated_data):
        menu_image_upload = validated_data.pop('menu_image_upload', None)
        # user = validated_data.pop('user')
        user = self.context["request"].user
        validated_data["restaurant"] = user.restaurant
        menu = Menu.objects.create(user=user, **validated_data)
        
        if menu_image_upload:
            upload = cloudinary.uploader.upload(
                menu_image_upload,
                folder="aptech_python_onlineFood_delivery/menus"
            )
            menu.menu_image = upload.get('secure_url')
            menu.save()
        return menu;
        # return super().create(validated_data)
    def update(self, instance, validated_data):
        menu_image_upload = validated_data.pop('menu_image_upload', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if menu_image_upload:
            upload = cloudinary.uploader.upload(
                menu_image_upload,
                folder='aptech_python_onlineFood_delivery/menus'
            )
            instance.menu_image = upload.get('secure_url')
        
        instance.save()
        return instance

    def validate(self, attrs):
        # nothing special here—restaurant is set to owner’s restaurant on create
        return attrs