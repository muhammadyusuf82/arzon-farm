from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Pharmacy, Drug, PharmacyStock, Cart
from .serializers import PharmacySerializer, DrugSerializer, PharmacyStockSerializer, CartSerializer

class DrugViewSet(viewsets.ModelViewSet):
    queryset=Drug.objects.all()
    serializer_class=DrugSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
    
class PharmacyViewSet(viewsets.ModelViewSet):
    queryset=Pharmacy.objects.all()
    serializer_class=PharmacySerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
    
class PharmacyStockView(viewsets.ModelViewSet):
    queryset=PharmacyStock.objects.all()
    serializer_class=PharmacyStockSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
    
class CartViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Cart.objects.filter(client=self.request.user)
    
    serializer_class=CartSerializer
    permission_classes=[IsAuthenticated]