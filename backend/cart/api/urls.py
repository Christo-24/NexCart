from django.urls import path
from .views import CartView, CartItemUpdateView, CartItemDeleteView, AddToCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('items/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    path('items/<int:pk>/delete/', CartItemDeleteView.as_view(), name='cart-item-delete'),
]