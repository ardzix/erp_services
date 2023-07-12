from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import ProductionOrder

@admin.register(ProductionOrder)
class ProductionOrderAdmin(BaseAdmin):
    list_display = ['product', 'quantity']
    list_filter = []
