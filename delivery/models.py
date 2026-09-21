from django.db import models
from django.contrib.auth import get_user_model
from pharmacies.models import Pharmacy, Cart, CartItem, PharmacyStock
# Create your models here.
User = get_user_model()
  
class Courier(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name="courier_profile")
    is_active=models.BooleanField(default=True)
    vehicle=models.CharField(max_length=150, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)  

class CourierRequest(models.Model):
    STATUS_CHOICES=(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    applicant=models.OneToOneField(User, on_delete=models.CASCADE, related_name='courier_request')
    status=models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    vehicle=models.CharField(max_length=150, blank=True)
    note=models.CharField(blank=True, help_text='applicants notes')
    created_at=models.DateTimeField(auto_now_add=True)
    reviewed_at=models.DateTimeField(null=True, blank=True)
    reviewed_by=models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"courier {self.pk} {self.applicant} {self.status}"
    
class Order(models.Model):
    DELIVERY_CHOICES = (
        ('self_delivery', 'Bron qilish (samovivoz)'),
        ('delivery', 'Yetkazib berish (dostavka)')
    )
    STATUS_CHOICES = (
        ('pending_receipt', 'Retsept kutilmoqda'),
        ('reviewing', 'Retsept tekshirilmoqda'),
        ('approved_assembling', 'Tasdiqlandi, joylanmoqda'), 
        ('ready', 'Olib ketish uchun tayyor'), 
        ('on_the_way', 'Yetkazib beruvchi yolda'),
        ('delivered', 'Yetkazildi'),
        ('rejected', 'Rad etildi'),
    )
    client=models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    pharmacy=models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='orders')
    cart=models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    courier=models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_type=models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    status=models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_receipt')
    prescription_image=models.ImageField(upload_to='receipts/', null=True, blank=True)
    delivery_address=models.TextField(blank=True)
    total_price=models.DecimalField(max_digits=15, decimal_places=3, default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"order {self.pk} {self.client} {self.status}"
    
    def calculate_total(self):
        total = sum(item.price * item.quantity for item in self.cart.items.all())
        self.total_price = total
        self.save(update_fields=['total_price'])
        return total
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    stock_item=models.ForeignKey(PharmacyStock, on_delete=models.PROTECT)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=15, decimal_places=3)