from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from cart.models import Cart
from ..models import Order, OrderItem
from .serializers import OrderSerializer

class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.create(user=request.user, total_amount=cart.total_price)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            )
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)