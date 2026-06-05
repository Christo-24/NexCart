from django.db import models
from django.conf import settings

class Order(models.Model):

    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),(COMPLETED, 'Completed'),(CANCELLED, 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name