from django.utils import timezone
from rest_framework import serializers
from .models import *
from pharmacies.models import *

class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model=Courier
        fields=['id', 'user', 'is_active', 'vehicle', 'created_at']
        read_only_fields=['user', 'created_at']
        
# class CourierRequest(serializers.ModelSerializer):
#     class Meta:
#         model=CourierRequest
#         fields=['id', 'applicant', 'status', 'vehicle', 'note', 'created_at', 'reviewed_at']
#         read_only_fields=['applicant', 'status', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=['id', 'stock_item', 'quantity', 'price']
        read_only_fields=['price']
        
class OrderSerializer(serializers.ModelSerializer):    
    order_items=OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model=Order
        fields=['id', 'client', 'pharmacy', 'cart', 'courier', 'delivery_type', 'status', 'prescription_image', 'delivery_address', 'total_price', 'created_at', 'updated_at', 'order_items']
        read_only_fields = ['client', 'pharmacy', 'cart', 'courier', 'status', 'total_price', 'created_at', 'updated_at']
        
class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id=serializers.PrimaryKeyRelatedField(queryset=Cart.objects.none(), source='cart', write_only=True)
    class Meta:
        model=Order
        fields=['cart_id', 'delivery_type', 'delivery_address', 'prescription_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request=self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['cart_id'].queryset=Cart.objects.filter(client=request.user, orders__isnull=True)
            
    def validate(self, attrs):
        if attrs.get('delivery_type') == 'delivery' and not attrs.get('delivery_address'):
            raise serializers.ValidationError({'delivery_address': 'this field is required for delivery orders'})
        return attrs
    
    def create(self, validated_data):
        cart: Cart=validated_data.pop('cart')
        request=self.context['request']
        order=Order.objects.create(
            client=request.user,
            pharmacy=cart.pharmacy,
            cart=cart,
            delivery_type=validated_data['delivery_type'],
            delivery_address=validated_data.get('delivery_address', ''),
            prescription_image=validated_data.get('prescription_image'),
            status='pending_receipt',
        )
        total=0
        for cart_item in cart.items.select_related('stock_item').all():
            price = cart_item.price_at_purchase
            OrderItem.objects.create(
                order=order,
                stock_item=cart_item.stock_item,
                quantity=cart_item.quantity,
                price=price
            )
            total+=price*cart_item.quantity
        order.total_price=total
        order.save(update_fields=['total_price'])
        return order
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['status', 'courier']
        
    def validate(self, attrs):
        order=self.instance
        new_status=attrs.get('status', order.status)
        new_courier=attrs.get('courier', order.courier)
        if new_courier and order.delivery_type != 'delivery':
            raise serializers.ValidationError({'courier':'courier can be assigned to the delivery orders'})
        if new_status=='on_the_way' and not (new_courier or order.courier):
            raise serializers.ValidationError({'courier':'courier must be assigned earlier'})
        return attrs 