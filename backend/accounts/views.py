from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from dj_rest_auth.utils import jwt_encode
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