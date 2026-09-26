from rest_framework import viewsets, exceptions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Pharmacy, Drug, PharmacyStock, Cart, Tag
from .serializers import PharmacySerializer, DrugSerializer, PharmacyStockSerializer, CartSerializer, TagSerializer
from .permissions import IsAdmin, IsPharmacyOwner, IsStockOwner, IsPharmacyUser

class TagViewSet(viewsets.ModelViewSet):
    queryset=Tag.objects.all()
    serializer_class=TagSerializer
    permission_classes=[IsAuthenticatedOrReadOnly, IsAdmin]

class DrugViewSet(viewsets.ModelViewSet):
    queryset=Drug.objects.all()
    serializer_class=DrugSerializer
    permission_classes=[IsAuthenticatedOrReadOnly, IsAdmin]
    
class PharmacyViewSet(viewsets.ModelViewSet):
    queryset=Pharmacy.objects.all()
    serializer_class=PharmacySerializer
    permission_classes=[IsAuthenticatedOrReadOnly, IsPharmacyOwner]  
    
    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Pharmacy.objects.all()
        if self.action in ['list', 'retrieve']: 
            return Pharmacy.objects.all()
        if user.is_authenticated:
            return Pharmacy.objects.filter(owner=user)
        return Pharmacy.objects.none()
    
    def perform_create(self, serializer):
        if Pharmacy.objects.filter(owner=self.request.user).exists():
            raise exceptions.ValidationError('you already have pharmacy accaunt')
        serializer.save(owner=self.request.user)
    
class PharmacyStockView(viewsets.ModelViewSet):
    serializer_class=PharmacyStockSerializer
    permission_classes=[IsAuthenticatedOrReadOnly, IsStockOwner]
    
    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return PharmacyStock.objects.all()
        if self.action in ['list', 'retrieve']:
            return PharmacyStock.objects.all()
        if user.is_authenticated:
            return PharmacyStock.objects.filter(pharmacy__owner=user)
        return PharmacyStock.objects.none()
    
    def perform_create(self, serializer):
        pharmacy=serializer.validated_data.get('pharmacy')
        if pharmacy.owner != self.request.user:
            raise exceptions.ValidationError('you are not the owner')
        serializer.save()
    
class CartViewSet(viewsets.ModelViewSet):
    serializer_class=CartSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.filter(client=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)