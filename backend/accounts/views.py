from rest_framework import generics, viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import LoginView
from django.shortcuts import get_object_or_404
from restaurants.models import Restaurant
from rest_framework.authtoken.models import Token
from accounts.models import CustomUser, Profile
from restaurants.serializers import RestaurantSerializer
from .serializers import ProfileSerializer

from .serializers import (
    CustomerRegisterSerializer,
    RestaurantOwnerRegisterSerializer,
    # LoginSerializer,
    UserSerializer,
)

# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#     }

class CustomerRegisterView(generics.CreateAPIView):
    serializer_class = CustomerRegisterSerializer
    permission_classes = [AllowAny]
    

class RestaurantOwnerRegisterView(generics.CreateAPIView,
                                ):
    serializer_class = RestaurantOwnerRegisterSerializer
    permission_classes = [AllowAny]

# class LoginView(generics.GenericAPIView):
#     """
#     Optional: if you want a custom login that returns token + user.
#     If you rely on dj_rest_auth /auth/login/, you can skip this and its URL.
#     """
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request):
#         ser = self.get_serializer(data=request.data)
#         ser.is_valid(raise_exception=True)
#         user = ser.validated_data["user"]

#         # If using TokenAuthentication
#         token, _ = Token.objects.get_or_create(user=user)

#         return Response({
#             "user": UserSerializer(user).data,
#             "token": token.key,
#         })


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class LoginView(LoginView):
    def get_response(self):
        response = super().get_response()
        data = response.data;

        # Get tokens
        access_token = data.get("access")
        refresh_token = data.get("refresh")
        
        
        if access_token:
            # Put access token in HttpOnly cookie
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=30000
            )
            
        if refresh_token:
            # You can store refresh token in backend DB, or also in cookie if needed
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=86400
            )
        return response;
    

class UserProfileViewMixin:
    """
    A mixin to retrieve either a user's personal profile or their restaurant profile
    based on their role.
    """
    def get_object(self):
        user = self.request.user
        
        if not user.is_authenticated:
            # For unauthenticated users, we don't have a profile to display.
            # You can handle this with permissions or return a 404.
            raise generics.Http404
        if user.role == CustomUser.Role.RESTAURANT_OWNER:
            # If the user is a restaurant owner, get their associated restaurant.
            # Assumes a OneToOneField from Restaurant to CustomUser with related_name="restaurant"
            return get_object_or_404(Restaurant, owner=user)
        else:
            # For all other roles (e.g., customer), get their personal profile.
            # Assumes a OneToOneField from Profile to CustomUser with related_name="profile"
            return get_object_or_404(Profile, user=user)
        
    def get_serializer_class(self):
        user = self.request.user
        if user.role == CustomUser.Role.RESTAURANT_OWNER:
            return RestaurantSerializer
        else:
            return ProfileSerializer


class ProfileCreateView(generics.CreateAPIView):
    """
    View to create a user's profile.
    This is a one-time operation for a user.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Check if the user already has a profile
        if hasattr(request.user, 'profile'):
            return Response(
                {"detail": "Profile already exists for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Manually link the profile to the current user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyProfileView(
    UserProfileViewMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    A view to retrieve and update the authenticated user's profile,
    which can be either a personal profile or a restaurant profile.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return super().get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)