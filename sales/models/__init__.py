from datetime import timedelta
from decimal import Decimal
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from libs.utils import get_config_value
from libs.base_model import BaseModelGeneric, User
from libs.constants import (WAITING, ON_PROGRESS, ARRIVED, COMPLETED, SKIPPED, VAT_DEFAULT)
from common.models import File, AdministrativeLvl1, AdministrativeLvl2, AdministrativeLvl3, AdministrativeLvl4
from inventory.models import Product, StockMovement, Unit, Warehouse
from identities.models import CompanyProfile

APPROVED_BY = 'Approved by'
APPROVED_AT = 'Approved at'
APPROVED_AT_HELP_TEXT = 'Specify the date and time of approval'
ORDER_OF_CUSTOMER_VISIT = 'Order of customer visit in the trip'
ENTER_THE = 'Enter the '


class StoreType(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_('Enter the store type name'))
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Store Type')
        verbose_name_plural = _('Store Types')


class Customer(BaseModelGeneric):
    CBD = 'cbd'
    COD = 'cod'
    CREDIT = 'credit'
    PAYMENT_TYPE_CHOICES = [
        (CBD, _('Cash before Delivery')),
        (COD, _('Cash on Delivery')),
        (CREDIT, _('Credit'))
    ]

    name = models.CharField(
        max_length=100, help_text=_('Enter the customer\'s name'))
    contact_number = models.CharField(
        max_length=15, help_text=_('Enter the contact number'))
    address = models.TextField(help_text=_('Enter the address'))
    location = models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_('Enter the location coordinates')
    )

    company_profile = models.ForeignKey(
        CompanyProfile,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='customers_profile',
        verbose_name=_('Company Profile'),
        help_text=_('Select the company profile associated with the customer')
    )
    administrative_lv1 = models.ForeignKey(AdministrativeLvl1, blank=True, null=True,
                                           on_delete=models.SET_NULL, help_text='%s %s' % (_(ENTER_THE), _('Administrative Lvl 1')))
    administrative_lv2 = models.ForeignKey(AdministrativeLvl2, blank=True, null=True,
                                           on_delete=models.SET_NULL, help_text='%s %s' % (_(ENTER_THE), _('Administrative Lvl 2')))
    administrative_lv3 = models.ForeignKey(AdministrativeLvl3, blank=True, null=True,
                                           on_delete=models.SET_NULL, help_text='%s %s' % (_(ENTER_THE), _('Administrative Lvl 3')))
    administrative_lv4 = models.ForeignKey(AdministrativeLvl4, blank=True, null=True,
                                           on_delete=models.SET_NULL, help_text='%s %s' % (_(ENTER_THE), _('Administrative Lvl 4')))
    rt = models.CharField(max_length=5, blank=True, null=True)
    rw = models.CharField(max_length=5, blank=True, null=True)
    store_name = models.CharField(
        blank=True, null=True, max_length=100, help_text=_('Enter the store name'))
    payment_type = models.CharField(
        max_length=25,  # Adjusting for the added descriptions
        choices=PAYMENT_TYPE_CHOICES,
        help_text=_('Select payment type.'),
        default=CBD,
        null=True,
        blank=True,
    )
    store_type = models.ForeignKey(StoreType, blank=True, null=True, on_delete=models.SET_NULL)
    id_card = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_id_card',
                                blank=True, null=True, on_delete=models.SET_NULL)
    store_front = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_store_front', blank=True, null=True, on_delete=models.SET_NULL)
    store_street = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_store_street', blank=True, null=True, on_delete=models.SET_NULL)
    signature = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_signature', blank=True, null=True, on_delete=models.SET_NULL)

    due_date = models.PositiveIntegerField(blank=True, null=True, help_text=_('Due date of credit payment in day.'))
    credit_limit_amount =  models.DecimalField(max_digits=19, decimal_places=2, default=0, help_text=_('Credit limit amount this customer can apply.'))
    credit_limit_qty = models.PositiveIntegerField(blank=True, null=True, help_text=_('Total credit qty this customer can apply.'))

    @property
    def province(self):
        return self.administrative_lv1.name if self.administrative_lv1 else "-"

    @property
    def city(self):
        return self.administrative_lv2.name if self.administrative_lv2 else "-"

    @property
    def district(self):
        return self.administrative_lv3.name if self.administrative_lv3 else "-"

    @property
    def location_coordinate(self):
        if self.location:
            return {
                'latitude': self.location.y,
                'longitude': self.location.x
            }
        return None

    def __str__(self):
        return _('Customer #{id32} [{name}]').format(id32=self.id32, name=self.name)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class SalesOrder(BaseModelGeneric):
    # Order Status Choices with Descriptions
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PROCESSING = 'processing'
    READY_TO_SHIP = 'ready_to_ship'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    STATUS_CHOICES = [
        (DRAFT, _('Draft: The initial stage of the order where it\'s still being drafted or created.')),
        (SUBMITTED, _('Submitted: Order has been completed and sent for review or approval.')),
        (APPROVED, _('Approved: Order has been accepted for processing after review.')),
        (REJECTED, _('Rejected: Order has been found unsuitable for processing and needs revision.')),
        (PROCESSING, _('Processing: Active steps to fulfill the order are underway.')),
        (READY_TO_SHIP, _('Ready for Shipping: Order is ready to be shipped.')),
        (SHIPPED, _('Shipped: Order has left the business premises and is en route to the customer.')),
        (DELIVERED, _(
            'Delivered: Order has reached its destination and is now with the customer.')),
        (COMPLETED, _(
            'Completed: All aspects of the order are done, and it\'s considered closed.')),
        (CANCELED, _('Canceled: Order was terminated before reaching completion.')),
    ]
    CANVASING = 'canvasing'
    TAKING_ORDER = 'taking_order'
    TYPE_CHOICES = [
        (CANVASING, _('Canvasing')),
        (TAKING_ORDER, _('Taking Order')),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        help_text=_('Select the customer associated with the order')
    )
    order_date = models.DateField(help_text=_('Enter the order date'))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sales_orders',
        verbose_name=_(APPROVED_BY),
        help_text=_('Select the user who approved the order')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(APPROVED_AT),
        help_text=_(APPROVED_AT_HELP_TEXT)
    )
    stock_movements = models.ManyToManyField(StockMovement, blank=True)
    # Add any other fields specific to your order model

    status = models.CharField(
        max_length=255,  # Adjusting for the added descriptions
        choices=STATUS_CHOICES,
        default=SUBMITTED,
        help_text=_('Current status of the sales order.')
    )
    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, default=TAKING_ORDER)
    invoice_pdf_generated = models.BooleanField(default=False)
    warehouse = models.ForeignKey(
        Warehouse, blank=True, null=True, on_delete=models.SET_NULL)
    visit = models.ForeignKey(
        'CustomerVisit', blank=True, null=True, on_delete=models.SET_NULL)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return _('Order #{id32} - {customer}').format(id32=self.id32, customer=self.customer)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    @property
    def delivery_status(self):
        return self.stock_movements.values_list('status', flat=True) if self.stock_movements.exists() else None

    @property
    def invoice(self):
        return Invoice.objects.filter(oerder=self).last()

    @property
    def customer_visits(self):
        return self.customervisit_set.all().order_by('-created_at')

    @property
    def subtotal(self):
       return self.invoice.subtotal
    
    @property
    def vat_percent(self):
        return self.invoice.vat_percent

    @property
    def vat_amount(self):
        return self.invoice.vat_amount

    @property
    def total(self):
        return self.invoice.total


class OrderItem(BaseModelGeneric):
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='order_items',  # Update the related_name
        related_query_name='orderitem',
        help_text=_('Select the order associated with the item')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text=_('Select the product associated with the item')
    )
    quantity = models.PositiveIntegerField(
        help_text=_('Enter the item quantity'))
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        help_text=_('Enter the item price in IDR (Rp)')
    )
    unit = models.ForeignKey(
        Unit, blank=True, null=True, on_delete=models.SET_NULL)
    # Add any other fields specific to your order item model

    def __str__(self):
        return _('Order Item #{id32} - [#{product_id32}]{product} ({quantity}{unit})').format(
            id32=self.id32,
            product=self.product.name,
            product_id32=self.product.id32,
            quantity=self.quantity,
            unit=self.unit.symbol
        )
    
    @property
    def total_price(self):
        return Decimal(self.quantity) * Decimal(self.price)

    @property
    def smallest_unit_quantity(self):
        return self.quantity * self.unit.conversion_to_top_level()

    class Meta:
        ordering = ['-id']
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')


class Invoice(BaseModelGeneric):
    order = models.OneToOneField(
        SalesOrder,
        on_delete=models.CASCADE,
        help_text=_('Select the order associated with the invoice')
    )
    invoice_date = models.DateField(help_text=_('Enter the invoice date'))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sales_invoices',
        verbose_name=_(APPROVED_BY),
        help_text=_('Select the user who approved the invoice')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(APPROVED_AT),
        help_text=_(APPROVED_AT_HELP_TEXT)
    )
    vat = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[
            MinValueValidator(0),  # minimum value is 0
            MaxValueValidator(1)   # maximum value is 1
        ],
        help_text=_('Value Added Tax percentage in decimal'))
    attachment = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_attachment', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def save(self, *args, **kwargs):
        # Check if vat is None and set default value
        if self.vat is None:
            self.vat = get_config_value('vat_percent', VAT_DEFAULT)

        super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return _('Invoice #{id32} - {order}').format(id32=self.id32, order=self.order)

    @property
    def customer(self):
        return self.order.customer

    @property
    def payment_status(self):
        payment = SalesPayment.objects.filter(invoice=self).last()
        return payment.status if payment else None

    @property
    def subtotal(self):
        amount = 0
        for item in self.order.order_items.all():
            amount += item.price * item.quantity
        return amount

    @property
    def vat_percent(self):
        return self.vat * 100

    @property
    def vat_amount(self):
        return Decimal(self.vat) * Decimal(self.subtotal)

    @property
    def total(self):
        return self.subtotal + self.vat_amount

    @property
    def payments(self):
        return self.salespayment_set.all().order_by('-created_at')


class SalesPayment(BaseModelGeneric):
    AUTHORIZE = 'authorize'
    CAPTURE = 'capture'
    SETTLEMENT = 'settlement'
    DENY = 'deny'
    PENDING = 'pending'
    CANCEL = 'cancel'
    REFUND = 'refund'
    EXPIRE = 'expired'
    FAILURE = 'falure'

    # STATUS_CHOICES
    STATUS_CHOICES = [
        (AUTHORIZE, _('Authorize: The payment has been authorized but not yet captured.')),
        (CAPTURE, _('Capture: The authorized payment has been secured.')),
        (SETTLEMENT, _('Settlement: The payment process has been completed and funds have been transferred.')),
        (DENY, _('Deny: The payment request was denied.')),
        (PENDING, _('Pending: The payment process is ongoing and the final status is not yet determined.')),
        (CANCEL, _('Cancel: The payment process was canceled before completion.')),
        (REFUND, _('Refund: Funds have been returned to the payer.')),
        (EXPIRE, _('Expired: The payment authorization has expired without capture.')),
        (FAILURE, _('Failure: The payment process encountered an error and was unsuccessful.'))
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        help_text=_('Select the invoice associated with the payment')
    )
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        help_text=_('Enter the payment amount')
    )
    payment_date = models.DateField(help_text=_('Enter the payment date'))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sales_payments',
        verbose_name=_(APPROVED_BY),
        help_text=_('Select the user who approved the payment')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(APPROVED_AT),
        help_text=_(APPROVED_AT_HELP_TEXT)
    )
    payment_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_payment_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=255,  # Adjusting for the added descriptions
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text=_('Current status of the payment.')
    )

    def __str__(self):
        return _('Payment #{id32} - {invoice}').format(id32=self.id32, invoice=self.invoice)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')


class TripTemplate(BaseModelGeneric):
    name = models.CharField(max_length=255, verbose_name=_(
        'Name'), help_text=_('Enter the name for the canvasing trip template'))
    customers = models.ManyToManyField(Customer, through='TripCustomer', verbose_name=_(
        'Customers'), help_text=_('Select customers for this trip template'))
    pic = models.ManyToManyField(User, blank=True, related_name='%(app_label)s_%(class)s_pic',
                                 help_text=_('Select people in charge of this trip'))
    collector_pic = models.ManyToManyField(User, blank=True, related_name='%(app_label)s_%(class)s_collector_pic',
                                           help_text=_('Select people in charge of this trip'))
    vehicles = models.ManyToManyField('logistics.Vehicle', blank=True, help_text=_(
        'Select vehicles prefered for this trip'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Trip Template')
        verbose_name_plural = _('Trip Templates')

    def generate_trips(self, start_date, end_date, salesperson, vehicle, type):
        generated_trips = []
        current_date = start_date
        while current_date <= end_date:
            trip = Trip.objects.create(
                template=self,
                date=current_date,
                salesperson=salesperson,
                vehicle=vehicle,
                type=type,
            )
            generated_trips.append(trip)
            current_date += timedelta(days=1)

        return generated_trips

    def __str__(self):
        return self.name


class TripCustomer(BaseModelGeneric):
    template = models.ForeignKey(
        TripTemplate, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(verbose_name=_(
        'Order'), help_text=_(ORDER_OF_CUSTOMER_VISIT))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Trip Customer')
        verbose_name_plural = _('Trip Customers')
        ordering = ['order']

    def __str__(self):
        return f'{self.template.name} - {self.customer.name}'


class Trip(BaseModelGeneric):
    CANVASING = 'canvasing'
    TAKING_ORDER = 'taking_order'
    COLLECTING = 'collecting'
    TYPE_CHOICES = [
        (CANVASING, _('Canvasing')),
        (TAKING_ORDER, _('Taking Order')),
        (COLLECTING, _('Collecting')),
    ]

    STATUS_CHOICES = [
        (WAITING, _('Waiting')),
        (ON_PROGRESS, _('On Progress')),
        (ARRIVED, _('Arrived')),
        (COMPLETED, _('Completed')),
        (SKIPPED, _('Skipped'))
    ]

    template = models.ForeignKey(
        TripTemplate, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_(
        'Date'), help_text=_('Date for the trip'))
    salesperson = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='trip_salesperson')
    collector = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name='trip_collector')
    vehicle = models.ForeignKey(
        'logistics.Vehicle', on_delete=models.SET_NULL, blank=True, null=True
    )
    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, default=TAKING_ORDER)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=WAITING)
    is_delivery_processed = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Trip')
        verbose_name_plural = _('Trips')

    def __str__(self):
        return f'#{self.id32} {self.type} of {self.template.name} on {self.date}'

    @property
    def stock_movement_id32s(self):
        visits = self.customervisit_set
        if not visits.exists():
            return []
        sales_order_ids = visits.values_list('sales_order', flat=True)
        sales_order = SalesOrder.objects.filter(id__in=sales_order_ids)
        return sales_order.values_list('stock_movements__id32', flat=True) if sales_order.exists() else []


class CustomerVisit(BaseModelGeneric):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sales_order = models.ForeignKey(
        SalesOrder, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=50, choices=Trip.STATUS_CHOICES, default=WAITING)
    order = models.PositiveIntegerField(verbose_name=_(
        'Order'), help_text=_(ORDER_OF_CUSTOMER_VISIT))

    visit_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_visit_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    item_delivery_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_item_delivery_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    signature = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_signature', blank=True, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name = _('Customer Visit')
        verbose_name_plural = _('Customer Visits')

    def __str__(self):
        return f'{self.trip} - {self.customer.name}'

    def sales_occurred(self):
        '''Checks if any sales occurred during this visit'''
        return self.sales_order is not None

    def get_sold_products(self):
        '''Retrieve products sold during this visit'''
        # Placeholder implementation, refine based on actual implementation
        if self.sales_order:
            return self.sales_order.order_items.all()
        return []


class CustomerVisitReport(BaseModelGeneric):
    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name='canvasing_reports')
    customer_visit = models.OneToOneField(
        CustomerVisit, on_delete=models.CASCADE, related_name='report')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15, choices=Trip.STATUS_CHOICES)
    sold_products = models.ManyToManyField(OrderItem, blank=True)

    def __str__(self):
        return f'Report for {self.customer} - {self.status}'

    class Meta:
        ordering = ['-id']
        verbose_name = _('Customer Visit Report')
        verbose_name_plural = _('Customer Visit Reports')
