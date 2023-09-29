from datetime import timedelta, date
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from common.models import File, AdministrativeLvl1, AdministrativeLvl2, AdministrativeLvl3, AdministrativeLvl4
from inventory.models import Product, StockMovement, Unit
from identities.models import CompanyProfile
from logistics.models import Vehicle

APPROVED_BY = 'Approved by'
APPROVED_AT = 'Approved at'
APPROVED_AT_HELP_TEXT = 'Specify the date and time of approval'
ORDER_OF_CUSTOMER_VISIT = 'Order of customer visit in the trip'


class Customer(BaseModelGeneric):
    PAYMENT_TYPE_CHOICES = [
        ('cbd', _('Cash before Delivery')),
        ('cod', _('Cash on Delivery')),
        ('credit', _('Credit'))
    ]
    STORE_TYPE_CHOICES = [
        ('wholesaler', _('Wholesaler')),
        ('distributor', _('Distributor')),
        ('retailer', _('Retailer')),
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
    administrative_lv1 = models.ForeignKey(AdministrativeLvl1, blank=True, null=True, on_delete=models.SET_NULL, help_text='%s %s' % (_('Enter the '), _('Administrative Lvl 1')))
    administrative_lv2 = models.ForeignKey(AdministrativeLvl2, blank=True, null=True, on_delete=models.SET_NULL, help_text='%s %s' % (_('Enter the '), _('Administrative Lvl 2')))
    administrative_lv3 = models.ForeignKey(AdministrativeLvl3, blank=True, null=True, on_delete=models.SET_NULL, help_text='%s %s' % (_('Enter the '), _('Administrative Lvl 3')))
    administrative_lv4 = models.ForeignKey(AdministrativeLvl4, blank=True, null=True, on_delete=models.SET_NULL, help_text='%s %s' % (_('Enter the '), _('Administrative Lvl 4')))
    rt = models.CharField(max_length=5, blank=True, null=True)
    rw = models.CharField(max_length=5, blank=True, null=True)
    store_name = models.CharField(
        blank=True, null=True, max_length=100, help_text=_('Enter the store name'))
    payment_type = models.CharField(
        max_length=25,  # Adjusting for the added descriptions
        choices=PAYMENT_TYPE_CHOICES,
        help_text=_('Select payment type.'),
        blank=True,
        null=True
    )
    store_type = models.CharField(
        max_length=25,  # Adjusting for the added descriptions
        choices=STORE_TYPE_CHOICES,
        help_text=_('Select store type.'),
        blank=True,
        null=True
    )

    id_card = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_id_card', blank=True, null=True, on_delete=models.SET_NULL)
    store_front = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_store_front', blank=True, null=True, on_delete=models.SET_NULL)
    store_street = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_store_street', blank=True, null=True, on_delete=models.SET_NULL)
    signature = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_signature', blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def location_coordinate(self):
        if self.location:
            return {
                'latitude': self.location.y,
                'longitude': self.location.x
            }
        return None

    def __str__(self):
        return _('Customer #{id32} - {name}').format(id32=self.id32, name=self.name)

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class SalesOrder(BaseModelGeneric):
    # Order Status Choices with Descriptions
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PROCESSING = 'processing'
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
        (SHIPPED, _('Shipped: Order has left the business premises and is en route to the customer.')),
        (DELIVERED, _(
            'Delivered: Order has reached its destination and is now with the customer.')),
        (COMPLETED, _(
            'Completed: All aspects of the order are done, and it\'s considered closed.')),
        (CANCELED, _('Canceled: Order was terminated before reaching completion.')),
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
    stock_movement = models.ForeignKey(
        StockMovement, blank=True, null=True, on_delete=models.SET_NULL)
    # Add any other fields specific to your order model

    status = models.CharField(
        max_length=255,  # Adjusting for the added descriptions
        choices=STATUS_CHOICES,
        default=DRAFT,
        help_text=_('Current status of the sales order.')
    )

    def __str__(self):
        return _('Order #{id32} - {customer}').format(id32=self.id32, customer=self.customer)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    @property
    def delivery_status(self):
        return self.stock_movement.status if self.stock_movement else None


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
        max_digits=10,
        decimal_places=2,
        help_text=_('Enter the item price in IDR (Rp)')
    )
    unit = models.ForeignKey(
        Unit, blank=True, null=True, on_delete=models.SET_NULL)
    # Add any other fields specific to your order item model

    def __str__(self):
        return _('Order Item #{id32} - {product} {quantity}({unit})').format(
            id32=self.id32,
            product=self.product.name,
            quantity=self.quantity,
            unit=self.product.sales_unit.symbol if self.product.sales_unit else '-'
        )

    class Meta:
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
    # Add any other fields specific to your invoice model

    def __str__(self):
        return _('Invoice #{id32} - {order}').format(id32=self.id32, order=self.order)

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')


class SalesPayment(BaseModelGeneric):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        help_text=_('Select the invoice associated with the payment')
    )
    amount = models.DecimalField(
        max_digits=10,
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
    # Add any other fields specific to your payment model

    def __str__(self):
        return _('Payment #{id32} - {invoice}').format(id32=self.id32, invoice=self.invoice)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')


class TripTemplate(BaseModelGeneric):
    name = models.CharField(max_length=255, verbose_name=_(
        'Name'), help_text=_('Enter the name for the canvasing trip template'))
    customers = models.ManyToManyField(Customer, through='TripCustomer', verbose_name=_(
        'Customers'), help_text=_('Select customers for this trip template'))

    class Meta:
        verbose_name = _('Trip Template')
        verbose_name_plural = _('Trip Templates')

    def generate_trips(self, start_date, end_date, salesperson, vehicle):
        generated_trips = []
        current_date = start_date
        while current_date <= end_date:
            trip = Trip.objects.create(
                template=self,
                date=current_date,
                salesperson=salesperson,
                vehicle=vehicle,
                # Assuming the template has a reference to the user who created it.
                created_by=self.created_by
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
        verbose_name = _('Trip Customer')
        verbose_name_plural = _('Trip Customers')
        ordering = ['order']

    def __str__(self):
        return f'{self.template.name} - {self.customer.name}'


class Trip(BaseModelGeneric):
    template = models.ForeignKey(
        TripTemplate, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_(
        'Date'), help_text=_('Date for the canvasing trip'))
    salesperson = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='canvasing_salesperson')
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, blank=True, null=True
    )
    
    CANVASING = 'canvasing'
    TAKING_ORDER = 'taking_order'
    COLLECTING = 'collecting'
    DELIVERING = 'delivering'
    TYPE_CHOICES = [
        (CANVASING, _('Canvasing')),
        (TAKING_ORDER, _('Taking Order')),
        (COLLECTING, _('Collecting')),
        (DELIVERING, _('Delivering'))
    ]
    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, default=TAKING_ORDER)

    WAITING = 'waiting'
    ON_PROGRESS = 'on_progress'
    ARRIVED = 'arrived'
    COMPLETED = 'completed'
    SKIPPED = 'skipped'

    STATUS_CHOICES = [
        (WAITING, _('Waiting')),
        (ON_PROGRESS, _('On Progress')),
        (ARRIVED, _('Arrived')),
        (COMPLETED, _('Completed')),
        (SKIPPED, _('Skipped'))
    ]

    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=WAITING)

    class Meta:
        verbose_name = _('Trip')
        verbose_name_plural = _('Trips')

    def __str__(self):
        return f'{self.template.name} on {self.date}'


class CustomerVisit(BaseModelGeneric):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sales_order = models.ForeignKey(
        SalesOrder, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=50, choices=Trip.STATUS_CHOICES, default=Trip.WAITING)
    order = models.PositiveIntegerField(verbose_name=_(
        'Order'), help_text=_(ORDER_OF_CUSTOMER_VISIT))

    visit_evidence = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_visit_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    signature = models.ForeignKey(File, related_name='%(app_label)s_%(class)s_signature', blank=True, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)

    class Meta:
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
        verbose_name = _('Customer Visit Report')
        verbose_name_plural = _('Customer Visit Reports')
