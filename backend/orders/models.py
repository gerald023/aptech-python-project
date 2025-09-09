from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, Dish
import uuid

User = settings.AUTH_USER_MODEL
# Create your models here.


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PREPARING = "preparing", "Preparing"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot of price at order time

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"
    


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot of dish price

    class Meta:
        unique_together = ("cart", "dish")  # ensures one row per dish per cart

    def __str__(self):
        return f"{self.dish.name} ({self.quantity})"

    @property
    def subtotal(self):
        return self.price * self.quantity

    def increase_quantity(self, qty=1):
        self.quantity += qty
        self.save()

    def decrease_quantity(self, qty=1):
        if self.quantity > qty:
            self.quantity -= qty
            self.save()
        else:
            self.delete()


class Transaction(models.Model):
    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="transaction")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)  # e.g. Paystack/Stripe reference
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.reference} - {self.status}"