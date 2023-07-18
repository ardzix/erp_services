from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from libs.admin import BaseAdmin

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
            ('customer', _('Customer')),
            ('supplier', _('Supplier')),
        )


class FromWarehouseFilter(WarehouseFilter):
    title = _('Origin Filter')  # Display name of the filter
    parameter_name = 'origin_filter'  # URL parameter name for the filter

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value():
            return queryset.filter(origin_type__model=self.value())
        return queryset

class ToWarehouseFilter(WarehouseFilter):
    title = _('Destination Filter')  # Display name of the filter
    parameter_name = 'destionation_filter'  # URL parameter name for the filter

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value():
            return queryset.filter(destionation_type__model=self.value())
        return queryset
    

class WarehouseTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the foreign key field
        ct = ContentType.objects.filter(model__in=['customer', 'supplier', 'warehouse'])
        self.fields['origin_type'].queryset = ct
        self.fields['destionation_type'].queryset = ct


@admin.register(StockMovement)
class StockMovementAdmin(BaseAdmin):
    form = WarehouseTypeForm
    list_display = ['id32', 'product', 'quantity', 'origin', 'destionation', 'status', 'movement_date']
    list_filter = ['movement_date', 'status', FromWarehouseFilter ,ToWarehouseFilter]
    search_fields = ['product__name']
    fields = ['product', 'quantity', 'status', 'movement_date', 'origin', 'origin_id', 'origin_type', 'destionation', 'destionation_id', 'destionation_type']
    readonly_fields = ['origin', 'destionation']

    def origin(self, obj):
        if obj.origin:
            return f"{obj.origin}"
        else:
            return ''

    def destionation(self, obj):
        if obj.destionation:
            return f"{obj.destionation}"
        else:
            return ''


    origin.short_description = _('Origin')
    destionation.short_description = _('Destination')


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
