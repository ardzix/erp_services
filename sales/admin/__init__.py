from django.contrib import admin
from django.db.models import Sum, F
from libs.admin import ApproveRejectMixin, BaseAdmin


from ..models import (
    TripTemplate,
    TripCustomer,
    Customer,
    Trip,
    CustomerVisit,
    CustomerVisitReport,
    Customer,
    SalesOrder,
    OrderItem,
    Invoice,
    SalesPayment)


@admin.register(Customer)
class CustomerAdmin(BaseAdmin):
    list_display = ['id32', 'name',
                    'contact_number', 'address', 'show_location']
    list_filter = ['company_profile']
    search_fields = ['name', 'contact_number', 'address']

    fields = ['name', 'contact_number', 'company_profile',
              'administrative_lv1', 'administrative_lv2', 'administrative_lv3', 'administrative_lv4',
              'rt', 'rw', 'store_name', 'payment_type', 'store_type',
              'id_card', 'store_front', 'store_street', 'signature',
              'address', 'location'
              ]
    raw_id_fields = ['administrative_lv1', 'administrative_lv2',
                     'administrative_lv3', 'administrative_lv4']

    def show_location(self, obj):
        return f"Latitude: {obj.location.y}, Longitude: {obj.location.x}" if obj.location else None
    show_location.short_description = 'Location'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['product']
    fields = ['product', 'quantity', 'price', 'unit']


@admin.register(SalesOrder)
class SalesOrderAdmin(ApproveRejectMixin, BaseAdmin):
    inlines = [OrderItemInline]
    list_display = ['id32', 'customer', 'order_date',
                    'approved_by', 'status', 'type']
    list_filter = ['customer', 'order_date', 'approved_by']
    search_fields = ['id32', 'customer__name']
    fields = ['customer', 'order_date', 'approved_by', 'approved_at', 'unapproved_by',
              'unapproved_at', 'status', 'type', 'invoice', 'warehouse', 'visit']
    readonly_fields = ['invoice']


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
        return instance.order.total


@admin.register(SalesPayment)
class SalesPaymentAdmin(BaseAdmin):
    list_display = ['id32', 'invoice', 'total_amount',
                    'payment_date', 'status']
    list_filter = ['invoice__order__customer', 'payment_date', 'approved_by']
    search_fields = ['id32', 'invoice__order__id32']
    fields = ['invoice', 'amount', 'payment_date', 'status', 'payment_evidence',
              'approved_by', 'approved_at']
    raw_id_fields = ['invoice']

    def total_amount(self, instance):
        return f'{instance.amount:,.0f}'


class TripCustomerInline(admin.TabularInline):
    model = TripCustomer
    fields = ('template', 'customer', 'order')
    raw_id_fields = ('customer', )
    extra = 0


class CustomerVisitInline(admin.TabularInline):
    model = CustomerVisit
    fields = ('customer', 'sales_order', 'status')
    raw_id_fields = ('customer', 'sales_order')
    extra = 0


@admin.register(TripTemplate)
class TripTemplateAdmin(BaseAdmin):
    list_display = ('id32', 'name')
    fields = ('name', 'pic', 'collector_pic', 'vehicles')
    search_fields = ('name',)
    raw_id_fields = ('pic', 'vehicles', 'collector_pic')
    inlines = [TripCustomerInline]


@admin.register(Trip)
class TripAdmin(BaseAdmin):
    list_display = ('id32', 'template', 'date',
                    'salesperson', 'collector', 'vehicle', 'status')
    fields = ('template', 'date', 'salesperson', 'vehicle', 'status')
    list_filter = ('status', 'date')
    search_fields = ('template__name',
                     'salesperson__username', 'vehicle__name')
    inlines = [CustomerVisitInline]


@admin.register(CustomerVisit)
class CustomerVisitAdmin(BaseAdmin):
    list_display = ('id32', 'trip', 'customer', 'sales_order', 'status')
    fields = ('trip', 'customer', 'sales_order', 'status', 'order',
              'visit_evidence', 'item_delivery_evidence', 'signature', 'notes')
    list_filter = ('status',)
    search_fields = ('trip__template__name', 'customer__name')


@admin.register(CustomerVisitReport)
class CustomerVisitReportAdmin(BaseAdmin):
    list_display = ('id32', 'trip', 'customer', 'status')
    fields = ('trip', 'customer_visit', 'customer', 'status', 'sold_products')
    list_filter = ('status',)
    search_fields = ('trip__template__name', 'customer__name')


@admin.register(TripCustomer)
class TripCustomerAdmin(BaseAdmin):
    list_display = ('id32', 'template', 'customer', 'order')
    fields = ('template', 'customer', 'order')
    search_fields = ('template__name', 'customer__name')
    raw_id_fields = ('customer', )
