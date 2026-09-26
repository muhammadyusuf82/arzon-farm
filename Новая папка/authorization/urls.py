from django.urls import path, include
from authorization.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('register/', register),
    path('view-profile/', view_profile),
    path('update-profile/', update_profile),
    path('change-password/', change_password),
    path('', include(router.urls)),
]
