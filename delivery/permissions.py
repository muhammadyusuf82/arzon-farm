from rest_framework import permissions

class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff: return True
        return obj.client == request.user

class IsPharmacyOrderManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff: return True
        return obj.pharmacy.owner == request.owner