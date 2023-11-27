from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem, Shipment, VendorPerformance

@admin.register(Supplier)
class SupplierAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'contact_number', 'address']
    list_filter = ['company_profile']
    fields = ['name', 'contact_number', 'address', 'location', 'company_profile']


@admin.register(SupplierProduct)
class SupplierProductAdmin(BaseAdmin):
    list_display = ['id32', 'supplier', 'product']
    list_filter = ['is_default_supplier']
    search_fields = ['supplier__name', 'product__name']
    fields = ['supplier', 'product', 'is_default_supplier']


class OrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    raw_id_fields = ['product']
    fields = ['product', 'quantity', 'po_price', 'actual_price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ApproveRejectMixin, BaseAdmin):
    inlines = [OrderItemInline]
    list_display = ['id32', 'supplier', 'order_date', 'approved_by', 'approved_at']
    list_filter = ['supplier', 'approved_by']
    fields = ['supplier', 'destination_warehouse', 'order_date', 'approved_by', 'approved_at', 'unapproved_by', 'unapproved_at']


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(BaseAdmin):
    list_display = ['id32', 'purchase_order', 'product', 'quantity', 'po_price']
    list_filter = ['purchase_order', 'product']
    fields = ['purchase_order', 'product', 'quantity', 'po_price']


@admin.register(Shipment)
class ShipmentAdmin(BaseAdmin):
    list_display = ['id32', 'purchase_order', 'shipment_date']
    list_filter = ['purchase_order']
    fields = ['purchase_order', 'shipment_date']

@admin.register(VendorPerformance)
class VendorPerformanceAdmin(BaseAdmin):
    list_display = ['id32', 'supplier', 'rating']
    list_filter = ['supplier', 'rating']
    fields = ['supplier', 'rating', 'comments']

