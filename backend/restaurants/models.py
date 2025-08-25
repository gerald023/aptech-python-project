from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# Create your models here.
class Restaurant(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="restaurant")
    name = models.CharField(max_length=255, default="Unnamed Restaurant")
    description = models.TextField(blank=True)
    menu_card_image = models.ImageField(upload_to="restaurants/menu_cards/", blank=True, null=True)
    # Add any branding fields you like

    def __str__(self):
        return self.name

class FoodType(models.Model):
    """
    Admin-defined types (Veg/Non-Veg etc.)
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="dishes/", blank=True, null=True)
    food_type = models.ForeignKey(FoodType, on_delete=models.SET_NULL, null=True, blank=True)

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"