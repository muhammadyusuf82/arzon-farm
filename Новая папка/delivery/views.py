from django.shortcuts import render
# from channels.layers import channel_layers
from .models import *
from .serializers import *
from .permissions import *
from rest_framework import viewsets, exceptions, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
# Create your views here.

class CourierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class=CourierSerializer
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff: return Courier.objects.select_related('user').all()
        return Courier.objects.select_related('user').filter(is_active=True)
    
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        user=self.request.user
        if user.is_staff: return Order.objects.select_related('client', 'pharmacy', 'courier').all()
        if hasattr(user, 'pharmacy_profile'): return Order.objects.filter(pharmacy=user.pharmacy_profile)
        return Order.objects.filter(client=user)
    
    def get_serializer_class(self):
        if self.action=='create': return OrderCreateSerializer
        if self.action=='update_status': return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        order=serializer.save()
    
    @action(detail=True, methods=['patch'], url_path='update-status', permission_classes=[IsAuthenticated, IsPharmacyOrderManager])
    def update_status(self, request, pk=None):
        order=self.get_object()
        serializer=OrderStatusUpdateSerializer(order, data=request.data, partial=True, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)    