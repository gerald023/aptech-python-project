from django.urls import path
from .views import CustomerRegisterView, RestaurantOwnerRegisterView, MeView

urlpatterns = [
    path("register/customer/", CustomerRegisterView.as_view(), name="register-customer"),
    path("register/restaurant-owner/", RestaurantOwnerRegisterView.as_view(), name="register-owner"),
    # path("login/", LoginView.as_view(), name="login-custom"),  # optional if using dj_rest_auth
    path("me/", MeView.as_view(), name="me"),
]