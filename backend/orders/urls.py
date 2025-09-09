from django.urls import path, include
from .views import OrderCreateView, MyOrdersView, RestaurantOrdersView, CartViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")


urlpatterns = [
    path("", include(router.urls)),
    path("create/", OrderCreateView.as_view(), name="order-create"),
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("restaurant-orders/", RestaurantOrdersView.as_view(), name="restaurant-orders"),
]