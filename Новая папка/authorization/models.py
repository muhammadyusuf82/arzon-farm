from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

user_roles = models.TextChoices('roles', 'user pharmacy courier')


class CustomUserManager(UserManager):
    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone_number must be set')
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        # AbstractUser still requires username; mirror phone_number
        extra_fields.setdefault('username', phone_number)

        user = self.model(phone_number=phone_number, email=email or '', **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, email=email, password=password, **extra_fields)


class User(AbstractUser):
    phone_number = models.CharField(max_length=9, null=False, blank=False, unique=True)
    role = models.CharField(choices=user_roles.choices, default='user', null=False, blank=False)
    metadata = models.JSONField(null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
