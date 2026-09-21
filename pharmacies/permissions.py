from rest_framework import permissions

class IsPharmacyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: 
            return True
        is_admin=request.user and request.user.is_staff
        is_owner=obj.owner==request.user
        return is_admin or is_owner

class IsStockOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: 
            return True
        is_admin=request.user and request.user.is_staff
        is_owner=request.user==obj.pharmacy.owner
        return is_admin or is_owner
    
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: 
            return True
        return request.user and request.user.is_staff
    
class IsPharmacyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method=='POST':
            return(
                request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'pharmacy'
            )
        return True