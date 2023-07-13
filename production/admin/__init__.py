from django.contrib import admin
from django.db.models import Sum, F
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import BillOfMaterials, BOMComponent, ProductionOrder, WorkOrder, ProductionTracking


class BOMComponentInline(admin.TabularInline):
    model = BOMComponent
    extra = 0
    raw_id_fields = ['component']
    fields = ['component', 'quantity']


@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(BaseAdmin):
    list_display = ['id32', 'product']
    search_fields = ['product__name']
    inlines = [BOMComponentInline]
    fields = ['product']
    raw_id_fields = ['product']


@admin.register(ProductionOrder)
class ProductionOrderAdmin(BaseAdmin):
    list_display = ['id32', 'product', 'quantity', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['id32', 'product__name']
    fields = ['product', 'quantity', 'start_date', 'end_date']
    raw_id_fields = ['product']


@admin.register(WorkOrder)
class WorkOrderAdmin(BaseAdmin):
    list_display = ['id32', 'production_order', 'operation_number', 'work_center', 'work_center_warehouse', 'assigned_to']
    list_filter = ['work_center', 'work_center_warehouse']
    search_fields = ['id32', 'production_order__product__name']
    fields = ['production_order', 'operation_number', 'work_center', 'work_center_warehouse', 'assigned_to']
    raw_id_fields = ['production_order', 'work_center_warehouse']


@admin.register(ProductionTracking)
class ProductionTrackingAdmin(BaseAdmin):
    list_display = ['id32', 'work_order', 'start_time', 'end_time', 'produced_quantity']
    list_filter = ['start_time', 'end_time']
    search_fields = ['id32', 'work_order__production_order__product__name']
    fields = ['work_order', 'start_time', 'end_time', 'produced_quantity']
    raw_id_fields = ['work_order']
