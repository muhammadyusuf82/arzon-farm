from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourierViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'couriers', CourierViewSet, basename='courier')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
