from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import BillOfMaterials, BOMProduct, BOMComponent, ProductionOrder, WorkOrder, ProductionTracking


class BOMProductInline(admin.TabularInline):
    model = BOMProduct
    extra = 0
    raw_id_fields = ['product']
    fields = ['product', 'quantity']

class BOMComponentInline(admin.TabularInline):
    model = BOMComponent
    extra = 0
    raw_id_fields = ['component']
    fields = ['component', 'quantity']


@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(BaseAdmin):
    list_display = ['id32', 'name']
    search_fields = ['name']
    inlines = [BOMComponentInline, BOMProductInline]
    fields = ['name']


@admin.register(ProductionOrder)
class ProductionOrderAdmin(BaseAdmin):
    list_display = ['id32', 'product', 'quantity', 'start_date', 'end_date', 'components']
    list_filter = ['start_date', 'end_date']
    search_fields = ['id32', 'product__name']
    fields = ['product', 'quantity', 'start_date', 'end_date']
    raw_id_fields = ['product']

    def components(self, obj):
        bom = BillOfMaterials.objects.get(products=obj.product)
        component_string = ''
        for component in BOMComponent.objects.filter(bom=bom):
            component_string += f'{component.component.name}: {component.quantity}pcs, '
        return component_string[:-2] if component_string != '' else component_string
    components.short_description = _('Components per quantity')


class WorkOrderStatusFilter(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        # Define the filter options and their display labels
        return (
            ('ordered', _('Ordered')),
            ('started', _('Started')),
            ('finished', _('Finished')),
        )
    title = _('Work Order Status Filter')  # Display name of the filter
    parameter_name = 'work_order_status_filter'  # URL parameter name for the filter

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value() == 'ordered':
            return queryset.filter(start_time__isnull=True)
        elif self.value() == 'started':
            return queryset.filter(start_time__isnull=False, end_time__isnull=True)
        elif self.value() == 'finished':
            return queryset.filter(end_time__isnull=False)
        return queryset



@admin.register(WorkOrder)
class WorkOrderAdmin(BaseAdmin):
    list_display = ['id32', 'production_order', 'quantity', 'operation_number', 'work_center', 'work_center_warehouse', 'end_time', 'assigned_to']
    list_filter = [WorkOrderStatusFilter, 'work_center', 'work_center_warehouse']
    search_fields = ['id32', 'production_order__product__name']
    fields = ['production_order', 'operation_number', 'work_center', 'work_center_warehouse', 'assigned_to', 'start_time', 'end_time']
    readonly_fields = ['end_time']
    raw_id_fields = ['production_order', 'work_center_warehouse']

    def quantity(self, obj):
        return obj.production_order.quantity


@admin.register(ProductionTracking)
class ProductionTrackingAdmin(BaseAdmin):
    list_display = ['id32', 'work_order', 'start_time', 'end_time', 'produced_quantity']
    list_filter = ['start_time', 'end_time']
    search_fields = ['id32', 'work_order__production_order__product__name']
    fields = ['work_order', 'start_time', 'end_time', 'produced_quantity']
    readonly_fields = ['start_time']
    raw_id_fields = ['work_order']
