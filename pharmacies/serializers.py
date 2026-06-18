from rest_framework import serializers
from .models import PharmacyStock

class CardItemSerializer(serializers.Serializer):
    stock_item_id=serializers.IntegerField()
    quantity=serializers.IntegerField(default=1)
    
    def validate(self, data):
        try:
            stock=PharmacyStock.objects.get(id=data['stock_item_id'])
        except PharmacyStock.DoesNotExist:
            raise serializers.ValidationError('item does not exist')
        
        if stock.quantity<data['quantity']:
            raise serializers.ValidationError('not enough stocks')
        
        data['stock_item'] = stock
        return data
    
    def to_representation(self, instance):
        stock=instance['stock_item']
        response={
            "stock_item":stock.id,
            "quantity":instance['quantity'],
            "is_prescription_required":stock.drug.is_prescription_required,
        }
        if stock.drug.is_prescription_required:
            response["warning_message"] = "Retsept talab qilinadi"
        return response
    