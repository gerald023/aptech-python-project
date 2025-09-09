from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Profile
from restaurants.models import Restaurant
import cloudinary.uploader



class ProfileSerializer(serializers.ModelSerializer):
    profile_picture_upload  = serializers.ImageField(write_only=True, required=False)
    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "display_name",
            "phone_number",
            "bio",
            "profile_picture",  # This field will display the Cloudinary URL
            "profile_picture_upload",
        ]
        
        read_only_fields = ["id", "user", "profile_picture"]
    def create(self, validated_data):
        profile_picture_upload = validated_data.pop("profile_picture_upload", None)
        user = validated_data.pop("user")
        profile = Profile.objects.create(user=user, **validated_data)
        
        if profile_picture_upload:
            upload = cloudinary.uploader.upload(
                profile_picture_upload,
                folder="aptech_python_onlineFood_delivery/profile_picture"
            )
            profile.profile_picture = upload.get("secure_url")  # cloudinary secure URL
            profile.save()
        return Profile
    
    def update(self, instance, validated_data):
        profile_picture_upload = validated_data.pop("profile_picture_upload", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if profile_picture_upload:
            upload = cloudinary.uploader.upload(
                profile_picture_upload,
                folder="aptech_python_onlineFood_delivery/profile_picture"
            )
            instance.profile_picture  = upload.get("secure_url")

        instance.save()
        return instance

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
