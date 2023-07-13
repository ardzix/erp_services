from django.contrib import admin
from django.db.models import Sum, F
from libs.admin import ApproveRejectMixin, BaseAdmin

from ..models import Customer, SalesOrder, OrderItem, Invoice, SalesPayment

@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'contact_number', 'address', 'show_location']
    list_filter = ['company_profile']
    search_fields = ['name', 'contact_number', 'address']
    fields = ['name', 'contact_number', 'address', 'location', 'company_profile']

    def show_location(self, obj):
        return f"Latitude: {obj.location.y}, Longitude: {obj.location.x}"
    show_location.short_description = 'Location'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['product']
    fields = ['product', 'quantity', 'price']

@admin.register(SalesOrder)
class SalesOrderAdmin(ApproveRejectMixin, BaseAdmin):
    inlines = [OrderItemInline]
    list_display = ['id32', 'customer', 'order_date', 'approved_by', 'total_amount']
    list_filter = ['customer', 'order_date', 'approved_by']
    search_fields = ['id32', 'customer__name']
    fields = ['customer', 'order_date', 'approved_by', 'approved_at', 'unapproved_by', 'unapproved_at']

    def total_amount(self, instance):
        total_amount = instance.orderitem_set.aggregate(total_price=Sum(F('price')*F('quantity'))).get('total_price')
        return f'{total_amount:,.0f}'

@admin.register(OrderItem)
class OrderItemAdmin(BaseAdmin):
    list_display = ['id32', 'order', 'product', 'quantity', 'price']
    list_filter = ['order']
    search_fields = ['id32', 'order__id32', 'product__name']
    fields = ['order', 'product', 'quantity', 'price']

@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    list_display = ['id32', 'order', 'invoice_date', 'total_amount']
    list_filter = ['order__customer', 'invoice_date', 'approved_by']
    search_fields = ['id32', 'order__id32']
    fields = ['order', 'invoice_date', 'approved_by', 'approved_at']
    raw_id_fields = ['order']

    def total_amount(self, instance):
        total_amount = instance.order.orderitem_set.aggregate(total_price=Sum(F('price')*F('quantity'))).get('total_price')
        return f'{total_amount:,.0f}'

@admin.register(SalesPayment)
class SalesPaymentAdmin(BaseAdmin):
    list_display = ['id32', 'invoice', 'total_amount', 'payment_date', 'approved_by', 'approved_at']
    list_filter = ['invoice__order__customer', 'payment_date', 'approved_by']
    search_fields = ['id32', 'invoice__order__id32']
    fields = ['invoice', 'amount', 'payment_date', 'approved_by', 'approved_at']
    raw_id_fields = ['invoice']

    def total_amount(self, instance):
        return f'{instance.amount:,.0f}'
