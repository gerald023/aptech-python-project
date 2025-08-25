from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, Dish

User = settings.AUTH_USER_MODEL
# Create your models here.


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PREPARING = "preparing", "Preparing"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def recalc_total(self):
        self.total_amount = sum(item.subtotal for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Order #{self.id} by {self.customer} from {self.restaurant}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot of price at order time

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"