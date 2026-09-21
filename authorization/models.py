from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

user_roles = models.TextChoices('roles', 'user pharmacy courier')

# Create your models here.

class CustomUserManager(UserManager):
    def create(self, *args, **kwargs):
        return super().create_user(*args, **kwargs)
    
    def create_user(self, email = ..., password = ..., **extra_fields):
        return super().create_user(extra_fields.get('phone_number'), email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        return super().create_superuser(extra_fields.get('phone_number'), email, password, **extra_fields)

class User(AbstractUser):

    phone_number = models.CharField(max_length=9, null=False, blank=False, unique=True)
    role = models.CharField(choices=user_roles.choices, default='user', null=False, blank=False)
    metadata = models.JSONField(null=True)

    USERNAME_FIELD = 'phone_number'
    
    objects = CustomUserManager()
