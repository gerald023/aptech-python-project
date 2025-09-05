from django.urls import path
from .views import CustomerRegisterView, RestaurantOwnerRegisterView, MeView, LoginView

urlpatterns = [
    path("register/customer/", CustomerRegisterView.as_view(), name="register-customer"),
    path("register/restaurant-owner/", RestaurantOwnerRegisterView.as_view(), name="register-owner"),
    path("login/", LoginView.as_view(), name="login-custom"),
    path("me/", MeView.as_view(), name="me"),
]