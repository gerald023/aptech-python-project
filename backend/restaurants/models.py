from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL


# Create your models here.
class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="restaurant")
    name = models.CharField(max_length=255, null=False, blank=False, default="Unnamed Restaurant")
    description = models.TextField(blank=True)
    restaurant_image = models.CharField(max_length=500, blank=True)
    # menu_card_image = models.ImageField(upload_to="restaurants/menu_cards/", blank=True, null=True)
    # # Add any branding fields you like

    def __str__(self):
        return self.name

class FoodType(models.Model):
    """
    Admin-defined types (Veg/Non-Veg etc.)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    
    
    def clean(self):
        allowed = {"Vegetarian", "Non-Vegetarian"}
        if self.name not in allowed:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"FoodType must be one of {allowed}")

    
    def __str__(self):
        return self.name

class Category(models.Model):
    """
    Categories like drink, soup, dessert, vegan, non-vegan, etc.
    Global + restaurant-specific categories.
    """
    GLOBAL_DEFAULTS = [
        "Drink", "Soup", "Dessert", "Meal",
        "Steak", "Vegan", "Non-Vegan"
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories"
    )  
    # If null → global category (available for all restaurants)

    class Meta:
        unique_together = ("name", "restaurant")

    def __str__(self):
        scope = self.restaurant.name if self.restaurant else "Global"
        return f"{self.name} ({scope})"


class Dish(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    dish_image = models.CharField(max_length=500, blank=True)
    food_type = models.ForeignKey(FoodType, on_delete=models.PROTECT)

    categories = models.ManyToManyField(Category, related_name="dishes", blank=True)
    menus = models.ManyToManyField("Menu", related_name="dishes", blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    


class Menu(models.Model):
    """
    A menu belongs to a restaurant, and can contain multiple dishes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menus"
    )
    name = models.CharField(max_length=255, default="Main Menu")
    menu_image = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("restaurant", "name")

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"