from rest_framework.permissions import BasePermission

class CanApprovePurchaseOrderPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('purchasing.approve_purchaseorder')
