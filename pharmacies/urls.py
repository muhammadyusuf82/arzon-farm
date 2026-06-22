from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router=DefaultRouter()
router.register(r'drugs', DrugViewSet, basename='drug')
router.register(r'pharmacies', PharmacyViewSet, basename='pharmacy')
router.register(r'stocks', PharmacyStockView, basename='stock')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls))
]
