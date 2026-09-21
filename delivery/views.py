from django.db.models import Q
from .models import *
from .serializers import *
from .permissions import *
from rest_framework import viewsets, exceptions, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CourierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Courier.objects.select_related('user').all()
        return Courier.objects.select_related('user').filter(is_active=True)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.select_related('client', 'pharmacy', 'courier').all()
        if hasattr(user, 'pharmacy_profile'):
            return Order.objects.filter(pharmacy=user.pharmacy_profile)
        if hasattr(user, 'courier_profile'):
            # courier sees his own orders + ready unassigned delivery orders
            return Order.objects.select_related('client', 'pharmacy', 'courier').filter(
                Q(courier=user.courier_profile) |
                Q(courier__isnull=True, status='ready', delivery_type='delivery')
            )
        return Order.objects.filter(client=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        # respond with the full order (incl. id), not the write-only serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='update-status',
            permission_classes=[IsAuthenticated, IsPharmacyOrderManager])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True,
                                                 context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        order = self.get_object()
        courier = getattr(request.user, 'courier_profile', None)
        if courier is None:
            raise exceptions.PermissionDenied('only couriers can accept orders')
        if order.courier is not None:
            raise exceptions.ValidationError({'courier': 'order already has a courier'})
        if order.status != 'ready' or order.delivery_type != 'delivery':
            raise exceptions.ValidationError({'status': 'order is not ready for pickup'})
        order.courier = courier
        order.status = 'on_the_way'
        order.save(update_fields=['courier', 'status'])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver(self, request, pk=None):
        order = self.get_object()
        courier = getattr(request.user, 'courier_profile', None)
        if courier is None or order.courier_id != courier.id:
            raise exceptions.PermissionDenied('only the assigned courier can deliver this order')
        order.status = 'delivered'
        order.save(update_fields=['status'])
        return Response(OrderSerializer(order).data)
