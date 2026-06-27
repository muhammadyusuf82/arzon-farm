from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
User=get_user_model()

class Pharmacy(models.Model):
    owner=models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy_profile')
    name=models.CharField(max_length=255)
    address=models.TextField()
    # phone_number=models.CharField(max_length=20)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name=models.CharField(max_length=100, unique=True)
    slug=models.SlugField(max_length=100, blank=True, null=True, unique=True)
    
    def __str__(self):
        return self.name

class Drug(models.Model):
    name=models.CharField(max_length=200)
    inn=models.CharField(max_length=200, help_text='International Nonproprietary Name')
    barcode=models.CharField(max_length=200, unique=True, blank=True, null=True)
    manufacturer=models.CharField(max_length=200)
    is_prescription_required=models.BooleanField(default=False)
    tags=models.ManyToManyField(Tag, blank=True, related_name='drugs')
    def __str__(self):
        return f"{self.name} ({self.inn})"
    
class PharmacyStock(models.Model):
    pharmacy=models.ForeignKey('Pharmacy', on_delete=models.CASCADE, related_name='inventory')
    drug=models.ForeignKey(Drug, on_delete=models.PROTECT, related_name='stocks')
    price=models.DecimalField(max_digits=10, decimal_places=3)
    quantity=models.IntegerField(default=0)
    is_available=models.BooleanField(default=True)
    
    class Meta:
        unique_together=('pharmacy', 'drug')
        
class Cart(models.Model):
    client=models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    pharmacy=models.ForeignKey('Pharmacy', on_delete=models.CASCADE, related_name='carts')
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"cart d"
    
    
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
    
    delivery_type=models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    status=models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_receipt')
    prescription_image=models.ImageField(upload_to='receipts/', null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    order=models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    stock_item=models.ForeignKey(PharmacyStock, on_delete=models.PROTECT)
    quantity=models.PositiveIntegerField(default=1)
    price_at_purchase=models.DecimalField(max_digits=10, decimal_places=3)
    
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