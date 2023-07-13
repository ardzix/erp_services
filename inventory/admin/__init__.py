from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.db.models import Q
from libs.admin import ApproveRejectMixin, BaseAdmin

from inventory.models import Category, Product, ProductLog, StockMovement, StockAdjustment, ReplenishmentOrder, ReplenishmentReceived, Warehouse, WarehouseStock


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'description']
    fields = ['name', 'description']


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'description', 'price', 'quantity', 'phsycal_quantity', 'category']
    list_filter = ['category']
    fields = ['name', 'description', 'price', 'quantity', 'phsycal_quantity', 'category']
    readonly_fields = ['phsycal_quantity']

    def phsycal_quantity(self, obj):
        return obj.phsycal_quantity


class WarehouseFilter(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        # Define the filter options and their display labels
        return (
            ('warehouse', _('Warehouse')),
            ('production', _('Production')),
            ('customer', _('Customer')),
            ('supplier', _('Supplier')),
        )


class FromWarehouseFilter(WarehouseFilter):
    title = _('From Warehouse Filter')  # Display name of the filter
    parameter_name = 'from_warehouse_filter'  # URL parameter name for the filter

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value():
            return queryset.filter(from_warehouse_type__model=self.value())
        return queryset

class ToWarehouseFilter(WarehouseFilter):
    title = _('To Warehouse Filter')  # Display name of the filter
    parameter_name = 'to_warehouse_filter'  # URL parameter name for the filter

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value():
            return queryset.filter(to_warehouse_type__model=self.value())
        return queryset


@admin.register(StockMovement)
class StockMovementAdmin(BaseAdmin):
    list_display = ['id32', 'product', 'quantity', 'from_warehouse', 'to_warehouse', 'movement_date']
    list_filter = ['movement_date', FromWarehouseFilter ,ToWarehouseFilter]
    search_fields = ['product__name']
    fields = ['product', 'quantity', 'from_warehouse', 'to_warehouse', 'movement_date']
    readonly_fields = ['from_warehouse', 'to_warehouse']

    def from_warehouse(self, obj):
        if obj.from_warehouse:
            return f"{obj.from_warehouse}"
        else:
            return ''

    def to_warehouse(self, obj):
        if obj.to_warehouse:
            return f"{obj.to_warehouse}"
        else:
            return ''


    from_warehouse.short_description = _('From Warehouse')
    to_warehouse.short_description = _('To Warehouse')


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(BaseAdmin):
    list_display = ['id32', 'product', 'quantity', 'adjustment_date', 'reason']
    list_filter = ['adjustment_date']
    fields = ['product', 'quantity', 'adjustment_date', 'reason']


@admin.register(ReplenishmentOrder)
class ReplenishmentOrderAdmin(BaseAdmin):
    list_display = ['id32', 'product', 'quantity', 'order_date']
    list_filter = ['order_date']
    fields = ['product', 'quantity', 'order_date']


@admin.register(ReplenishmentReceived)
class ReplenishmentReceivedAdmin(BaseAdmin):
    list_display = ['id32', 'replenishment_order', 'received_date']
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
    list_display = ['id32', 'name', 'address', 'location']
    fields = ['name', 'address', 'location']


@admin.register(WarehouseStock)
class WarehouseStockAdmin(BaseAdmin):
    list_display = ['id32', 'warehouse', 'product', 'quantity']
    list_filter = ['warehouse', 'product']
    fields = ['warehouse', 'product', 'quantity']
