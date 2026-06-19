from rest_framework import serializers
from .models import *

class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = '__all__'
class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'
        read_only_fields = ['owner']
class PharmacyStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyStock
        fields = '__all__'
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'stock_item', 'quantity', 'price_at_purchase']
        read_only_fields = ['price_at_purchase']
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'client', 'pharmacy', 'delivery_type', 'status', 'created_at', 'items']
        read_only_fields = ['client', 'status', 'created_at']