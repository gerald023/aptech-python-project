from django.contrib import admin
from .models import Restaurant, FoodType, Dish
# Register your models here.

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")

@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "food_type", "is_available")
    list_filter = ("restaurant", "food_type", "is_available")
    search_fields = ("name",)

# admin.site.register(Restaurant);
