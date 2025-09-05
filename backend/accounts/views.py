from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import LoginView
from rest_framework.authtoken.models import Token

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
    

class RestaurantOwnerRegisterView(generics.CreateAPIView):
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