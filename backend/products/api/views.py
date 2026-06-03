from rest_framework import generics
from products.models import Product
from .serializers import ProductSerializer 

from rest_framework.permissions import IsAuthenticated
from products.permissions import IsSeller

class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    serializer_class=ProductSerializer
    permission_classes=[
        IsAuthenticated,IsSeller
    ]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)