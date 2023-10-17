from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from libs.admin import BaseAdmin

from inventory.models import Category, Unit, Product, ProductGroup, ProductLog, StockMovement, StockMovementItem, StockAdjustment, ReplenishmentOrder, ReplenishmentReceived, Warehouse, WarehouseStock


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'description']
    fields = ['name', 'description']


@admin.register(Unit)
class UnitAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'symbol']
    fields = ['name', 'symbol', 'conversion_factor', 'parent']


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'description',
                    'base_price', 'quantity', 'phsycal_quantity', 'category']
    list_filter = ['category']
    fields = [
        'name', 'alias', 'sku', 'description', 'base_price', 'last_buy_price',
        'previous_buy_price', 'margin_type', 'margin_value', 'sell_price', 'quantity',
        'minimum_quantity', 'category', 'smallest_unit', 'purchasing_unit',
        'product_type', 'price_calculation', 'brand', 'picture',
        'phsycal_quantity', 'phsycal_quantity_amount', 'prices']
    readonly_fields = ['phsycal_quantity',
                       'phsycal_quantity_amount', 'previous_buy_price', 'prices']

    def phsycal_quantity(self, obj):
        return obj.phsycal_quantity

    def phsycal_quantity_amount(self, obj):
        return obj.phsycal_quantity_amount

    def prices(self, obj):
        return obj.prices


@admin.register(ProductGroup)
class ProductGroupAdmin(BaseAdmin):
    list_display = ['id32', 'name']
    fields = ['name', 'products', 'parent']


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
    parameter_name = 'destination_filter'  # URL parameter name for the filter

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value():
            return queryset.filter(destination_type__model=self.value())
        return queryset


class WarehouseTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the queryset for the foreign key field
        ct = ContentType.objects.filter(
            model__in=['customer', 'supplier', 'warehouse'])
        self.fields['origin_type'].queryset = ct
        self.fields['destination_type'].queryset = ct


class StockMovementItemInline(admin.TabularInline):
    model = StockMovementItem
    extra = 1
    fields = ['product', 'quantity', 'buy_price']
    raw_id_fields = ['product']
    verbose_name_plural = _("Stock Movement Items")


@admin.register(StockMovement)
class StockMovementAdmin(BaseAdmin):
    form = WarehouseTypeForm
    list_display = ['id32', 'origin', 'destination', 'status', 'movement_date']
    list_filter = ['movement_date', 'status',
                   FromWarehouseFilter, ToWarehouseFilter]
    search_fields = ['product__name']
    fields = ['status', 'movement_date', 'origin', 'origin_id',
              'origin_type', 'destination', 'destination_id', 'destination_type']
    readonly_fields = ['origin', 'destination']
    inlines = [StockMovementItemInline]

    def origin(self, obj):
        if obj.origin:
            return f"{obj.origin}"
        else:
            return ''

    def destination(self, obj):
        if obj.destination:
            return f"{obj.destination}"
        else:
            return ''

    origin.short_description = _('Origin')
    destination.short_description = _('Destination')


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
    list_display = ['product', 'quantity_change', 'buy_price_change',
                    'base_price_change', 'sell_price_change', 'created_at', 'created_by']
    list_filter = ['product']
    readonly_fields = ['product', 'quantity_change', 'buy_price_change',
                       'base_price_change', 'sell_price_change', 'created_at', 'created_by']
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
    list_display = ['id32', 'warehouse', 'product', 'quantity', 'unit']
    list_filter = ['warehouse', 'product']
    fields = ['warehouse', 'product', 'quantity', 'unit',
              'expire_date', 'inbound_movement_item', 'dispatch_movement_items']
