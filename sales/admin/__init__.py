from django.contrib import admin
from django.db.models import Sum, F
from libs.admin import ApproveRejectMixin, BaseAdmin


from ..models import (
    CanvasingTripTemplate,
    CanvasingCustomer,
    CanvasingCustomerProduct,
    CanvasingTrip,
    CanvasingCustomerVisit,
    CanvasingReport,
    Customer, 
    SalesOrder, 
    OrderItem, 
    Invoice, 
    SalesPayment)

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
        # total_amount = instance.orderitem_set.aggregate(total_price=Sum(F('price')*F('quantity'))).get('total_price')
        total_amount = 0
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



class CanvasingCustomerInline(admin.TabularInline):
    model = CanvasingCustomer
    fields = ('template', 'customer', 'order')
    raw_id_fields = ('customer', )
    extra = 0

class CanvasingCustomerProductInline(admin.TabularInline):
    model = CanvasingCustomerProduct
    fields = ('canvasing_customer', 'product', 'quantity')
    raw_id_fields = ('product', )
    extra = 0

class CanvasingCustomerVisitInline(admin.TabularInline):
    model = CanvasingCustomerVisit
    fields = ('customer', 'sales_order', 'status')
    raw_id_fields = ('customer', 'sales_order')
    extra = 0


@admin.register(CanvasingTripTemplate)
class CanvasingTripTemplateAdmin(BaseAdmin):
    list_display = ('id32', 'name')
    fields = ('name',)
    inlines = [CanvasingCustomerInline]
    search_fields = ('name',)

@admin.register(CanvasingTrip)
class CanvasingTripAdmin(BaseAdmin):
    list_display = ('id32', 'template', 'date', 'salesperson', 'driver', 'status')
    fields = ('template', 'date', 'salesperson', 'driver', 'status')
    list_filter = ('status', 'date')
    search_fields = ('template__name', 'salesperson__username', 'driver__username')
    inlines = [CanvasingCustomerVisitInline]

@admin.register(CanvasingCustomerVisit)
class CanvasingCustomerVisitAdmin(BaseAdmin):
    list_display = ('id32', 'trip', 'customer', 'sales_order', 'status')
    fields = ('trip', 'customer', 'sales_order', 'status')
    list_filter = ('status',)
    search_fields = ('trip__template__name', 'customer__name')

@admin.register(CanvasingReport)
class CanvasingReportAdmin(BaseAdmin):
    list_display = ('id32', 'trip', 'customer', 'status')
    fields = ('trip', 'customer_visit', 'customer', 'status', 'sold_products')
    list_filter = ('status',)
    search_fields = ('trip__template__name', 'customer__name')

class CanvasingCustomerProductInline(admin.TabularInline):
    model = CanvasingCustomerProduct
    fields = ('product', 'quantity')
    extra = 1
    raw_id_fields = ('product', )

@admin.register(CanvasingCustomer)
class CanvasingCustomerAdmin(BaseAdmin):
    list_display = ('id32', 'template', 'customer', 'order')
    fields = ('template', 'customer', 'order')
    inlines = [CanvasingCustomerProductInline]
    search_fields = ('template__name', 'customer__name')
    raw_id_fields = ('customer', )