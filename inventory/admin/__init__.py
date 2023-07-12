from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin

from inventory.models import Category, Product, ProductLog, StockMovement, StockAdjustment, ReplenishmentOrder, ReplenishmentReceived, Warehouse, WarehouseStock


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ['name', 'description']
    fields = ['name', 'description']


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ['name', 'description', 'price', 'quantity', 'phsycal_quantity', 'category']
    list_filter = ['category']
    fields = ['name', 'description', 'price', 'quantity', 'phsycal_quantity', 'category']
    readonly_fields = ['phsycal_quantity']

    def phsycal_quantity(self, obj):
        return obj.phsycal_quantity


@admin.register(StockMovement)
class StockMovementAdmin(BaseAdmin):
    list_display = ['product', 'quantity', 'from_warehouse', 'to_warehouse', 'movement_date']
    list_filter = ['movement_date']
    fields = ['product', 'quantity', 'from_warehouse', 'to_warehouse', 'movement_date']
    readonly_fields = ['from_warehouse', 'to_warehouse']

    def from_warehouse(self, obj):
        if obj.from_warehouse:
            return f"{obj.from_warehouse} ({obj.from_warehouse_type.model})"
        else:
            return ''

    def to_warehouse(self, obj):
        if obj.to_warehouse:
            return f"{obj.to_warehouse} ({obj.to_warehouse_type.model})"
        else:
            return ''


    from_warehouse.short_description = _('From Warehouse')
    to_warehouse.short_description = _('To Warehouse')


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(BaseAdmin):
    list_display = ['product', 'quantity', 'adjustment_date', 'reason']
    list_filter = ['adjustment_date']
    fields = ['product', 'quantity', 'adjustment_date', 'reason']


@admin.register(ReplenishmentOrder)
class ReplenishmentOrderAdmin(BaseAdmin):
    list_display = ['product', 'quantity', 'order_date']
    list_filter = ['order_date']
    fields = ['product', 'quantity', 'order_date']


@admin.register(ReplenishmentReceived)
class ReplenishmentReceivedAdmin(BaseAdmin):
    list_display = ['replenishment_order', 'received_date']
    list_filter = ['received_date']
    fields = ['replenishment_order', 'received_date']


@admin.register(ProductLog)
class ProductLogAdmin(BaseAdmin):
    list_display = ['product', 'quantity_change', 'created_at', 'created_by']
    list_filter = ['product']
    readonly_fields = ['product', 'quantity_change', 'created_at', 'created_by']
    ordering = ['-created_at']
    search_fields = ['product__name']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Warehouse)
class WarehouseAdmin(BaseAdmin):
    list_display = ['name', 'address', 'location']
    fields = ['name', 'address', 'location']


@admin.register(WarehouseStock)
class WarehouseStockAdmin(BaseAdmin):
    list_display = ['warehouse', 'product', 'quantity']
    list_filter = ['warehouse', 'product']
    fields = ['warehouse', 'product', 'quantity']
