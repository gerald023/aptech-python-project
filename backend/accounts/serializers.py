from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Profile
from restaurants.models import Restaurant



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["display_name", "phone_number", "bio", "profile_picture"]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "role", "profile"]
        

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "password"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=CustomUser.Role.CUSTOMER,
        )
        return user

class RestaurantOwnerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    restaurant_name = serializers.CharField(write_only=True)
    restaurant_description = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "restaurant_name", "restaurant_description"]

    def create(self, validated_data):
        name = validated_data.pop("restaurant_name")
        desc = validated_data.pop("restaurant_description", "")
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=CustomUser.Role.RESTAURANT_OWNER,
        )
        # Auto-create the restaurant (1–1 with owner)
        Restaurant.objects.create(owner=user, name=name, description=desc)
        return user



# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(email=data["email"], password=data["password"])
#         if not user:
#             raise serializers.ValidationError("Invalid credentials")
#         if not user.is_active:
#             raise serializers.ValidationError("User is inactive")
#         data["user"] = user
#         return data
