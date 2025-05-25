from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation


class Room(models.Model):
    ROOM_TYPES = (
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
    )
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_type} - {self.room_number}"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()

    def __str__(self):
        return f"{self.name} (₹{self.price})"

class FoodOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.FloatField() 
    order_date = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        try:
            return Decimal(self.quantity) * Decimal(self.price)
        except (InvalidOperation, TypeError, ValueError):
            return Decimal(0)

class Bill(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    customer = models.OneToOneField("Customer", on_delete=models.CASCADE)
    room_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    food_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill for {self.customer.name}"
