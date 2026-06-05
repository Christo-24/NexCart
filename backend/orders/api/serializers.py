from rest_framework import serializers
from orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'status', 'created_at', 'items']