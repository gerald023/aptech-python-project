from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet, FoodTypeViewSet, CategoryViewSet, MenuViewSet, RestaurantView
from . import views

router = DefaultRouter()
# router.register(r"dishes", DishViewSet, basename="dish")
router.register(r"foodtypes", FoodTypeViewSet, basename="foodtype")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"menus", MenuViewSet, basename="menu")
router.register(r"dishes", DishViewSet, basename="dish")
menu_list = MenuViewSet.as_view({'get': 'list', 'post': 'create'
})
menu_detail = MenuViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

# custom endpoints
public_menus = MenuViewSet.as_view({
    'get': 'public_menus'
})
by_restaurant = MenuViewSet.as_view({
    'get': 'by_restaurant'
})

# dish_list = DishViewSet.as_view({"get": "list", "post": "create"})
# dish_detail = DishViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"})
# dish_mine = DishViewSet.as_view({"get": "mine"})
# dish_add_to_menu = DishViewSet.as_view({"post": "add_to_menu"})
# dish_remove_from_menu = DishViewSet.as_view({"post": "remove_from_menu"})

urlpatterns = [
    path("", include(router.urls)),
    # path("dishes/", dish_list, name="dish-list"),
    # path("dishes/mine/", dish_mine, name="dish-mine"),
    # path("dishes/<uuid:pk>/", dish_detail, name="dish-detail"),
    # path("dishes/<uuid:pk>/add-to-menu/", dish_add_to_menu, name="dish-add-to-menu"),
    # path("dishes/<uuid:pk>/remove-from-menu/", dish_remove_from_menu, name="dish-remove-from-menu"),
    path("edit/", RestaurantView.as_view(), name="edit_restaurant_infos"),
    path("edit/<uuid:pk>/", RestaurantView.as_view(), name="edit_restaurant-detail"),
    path('menus/', menu_list, name='menu-list'),
    path('menus/<uuid:pk>/', menu_detail, name='menu-detail'),
    path('menus/public/', public_menus, name='menu-public'),
    path('menus/by-restaurant/<uuid:restaurant_id>/', by_restaurant, name='menus-by-restaurant'),
    path('all-restaurants/', views.RestaurantMixin.as_view()),
    path('<uuid:pk>/restaurant_details/', views.RestaurantMixin.as_view()),
    path('food_type/', views.FoodTypeView.as_view()),
    path('<uuid:pk>/food_type/', views.FoodTypeView.as_view()),
]