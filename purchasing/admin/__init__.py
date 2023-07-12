from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import Supplier, PurchaseOrder, PurchaseOrderItem, Shipment, VendorPerformance

@admin.register(Supplier)
class SupplierAdmin(BaseAdmin):
    list_display = ['name', 'contact_number', 'address']
    list_filter = ['company_profile']
    fields = ['name', 'contact_number', 'address', 'location', 'company_profile']


class OrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    raw_id_fields = ['product']
    fields = ['product', 'quantity', 'price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ApproveRejectMixin, BaseAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'supplier', 'order_date', 'approved_by', 'approved_at']
    list_filter = ['supplier', 'approved_by']
    fields = ['supplier', 'order_date', 'approved_by', 'approved_at', 'unapproved_by', 'unapproved_at']


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(BaseAdmin):
    list_display = ['id', 'purchase_order', 'product', 'quantity', 'price']
    list_filter = ['purchase_order', 'product']
    fields = ['purchase_order', 'product', 'quantity', 'price']


@admin.register(Shipment)
class ShipmentAdmin(BaseAdmin):
    list_display = ['id', 'purchase_order', 'shipment_date']
    list_filter = ['purchase_order']
    fields = ['purchase_order', 'shipment_date']

@admin.register(VendorPerformance)
class VendorPerformanceAdmin(BaseAdmin):
    list_display = ['id', 'supplier', 'rating']
    list_filter = ['supplier', 'rating']
    fields = ['supplier', 'rating', 'comments']

