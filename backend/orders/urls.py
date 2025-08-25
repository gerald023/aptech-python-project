from django.urls import path
from .views import OrderCreateView, MyOrdersView, RestaurantOrdersView

urlpatterns = [
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("mine/", MyOrdersView.as_view(), name="my-orders"),
    path("restaurant/", RestaurantOrdersView.as_view(), name="restaurant-orders"),
]