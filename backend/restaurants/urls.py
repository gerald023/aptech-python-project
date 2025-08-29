from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet
from . import views

router = DefaultRouter()
router.register(r"dishes", DishViewSet, basename="dish")

urlpatterns = [
    path("", include(router.urls)),
    path('all-restaurants/', views.RestaurantMixin.as_view()),
    path('<int:pk>/restaurant_details/', views.RestaurantMixin.as_view()),
    path('food_type/', views.FoodTypeView.as_view()),
    path('<int:pk>/food_type/', views.FoodTypeView.as_view()),
]  