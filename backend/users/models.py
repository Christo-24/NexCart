from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    BUYER = 'buyer'
    SELLER = 'seller'

    ROLE_CHOICES = [
        (BUYER, 'Buyer'),(SELLER, 'Seller'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BUYER)