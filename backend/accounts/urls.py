from django.urls import path, include
from .views import CustomerRegisterView, RestaurantOwnerRegisterView, MeView, LoginView
from rest_framework.routers import DefaultRouter
from .views import MyProfileView, ProfileCreateView

router = DefaultRouter();

router.register(r'my-profile', MyProfileView, basename='my-profile')


urlpatterns = [
    path("register/customer/", CustomerRegisterView.as_view(), name="register-customer"),
    path("register/restaurant-owner/", RestaurantOwnerRegisterView.as_view(), name="register-owner"),
    path("login/", LoginView.as_view(), name="login-custom"),
    path("me/", MeView.as_view(), name="me"),
    path('create-profile/', ProfileCreateView.as_view(), name='create-profile'),
    path('', include(router.urls)),
]