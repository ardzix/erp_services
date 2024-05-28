from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from libs.base_model import BaseModelGeneric, User
from common.models import File
from inventory.models import Product, StockMovement, Unit, Warehouse


class Supplier(BaseModelGeneric):
    PAYMENT_TERM_CASH = 0
    PAYMENT_TERM_7_DAYS = 7
    PAYMENT_TERM_14_DAYS = 14
    PAYMENT_TERM_21_DAYS = 21
    PAYMENT_TERM_30_DAYS = 30

    PAYMENT_TERMS_CHOICES = [
        (PAYMENT_TERM_CASH, 'Tunai'),
        (PAYMENT_TERM_7_DAYS, '7 Hari'),
        (PAYMENT_TERM_14_DAYS, '14 Hari'),
        (PAYMENT_TERM_21_DAYS, '21 Hari'),
        (PAYMENT_TERM_30_DAYS, '1 Bulan'),
    ]

    name = models.CharField(
        max_length=100,
        help_text=_("Enter the supplier's name")
    )
    contact_number = models.CharField(
        max_length=15,
        help_text=_("Enter the contact number")
    )
    address = models.TextField(
        help_text=_("Enter the address")
    )
    location = models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_("Enter the location coordinates")
    )
    company_profile = models.ForeignKey(
        'identities.CompanyProfile',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='suppliers_profile',
        verbose_name=_("Company Profile"),
        help_text=_("Select the company profile for this supplier")
    )
    payment_term = models.IntegerField(choices=PAYMENT_TERMS_CHOICES,
                                       default=PAYMENT_TERM_CASH,
                                       help_text="Enter payment term to decide billing date Purchase Order")
    has_payable = models.BooleanField(default=False)

    def get_payment_term_display(self):
        return dict(self.PAYMENT_TERMS).get(self.payment_term, 'Unknown')

    def __str__(self):
        return _("Supplier #{id32} - {name}").format(id32=self.id32, name=self.name)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")


class SupplierProduct(BaseModelGeneric):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        help_text=_("Select the supplier for this product")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text=_("Select the product provided by the supplier")
    )
    is_default_supplier = models.BooleanField(
        default=False,
        help_text=_(
            "Check if this supplier is the default supplier for the product")
    )

    def __str__(self):
        return _("{supplier} - {product}").format(supplier=self.supplier, product=self.product)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Supplier Product")
        verbose_name_plural = _("Supplier Products")
        unique_together = ['supplier', 'product']  # Ensure uniqueness


class PurchaseOrder(BaseModelGeneric):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        help_text=_("Select the supplier associated with the order")
    )
    order_date = models.DateField(
        help_text=_("Enter the order date")
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_orders',
        verbose_name=_("Approved by"),
        help_text=_("Select the user who approved the purchase order")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved at"),
        help_text=_("Specify the date and time when the order was approved")
    )
    stock_movement = models.ForeignKey(
        StockMovement, blank=True, null=True, on_delete=models.SET_NULL)
    destination_warehouse = models.ForeignKey(
        Warehouse, blank=True, null=True, on_delete=models.SET_NULL
    )
    invalid_item_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_invalid_item_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        help_text=_("Enter the discount amount for purchase order")
    )
    tax_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        help_text=_("Enter the tax amount for purchase order")
    )
    billing_due_date = models.DateField(default=now)
    down_payment = models.DecimalField(max_digits=19,
                                       decimal_places=2,
                                       default=0,
                                       help_text=_('Enter the DP amount'))
    down_payment_date = models.DateField(null=True, blank=True, help_text=_(
        "Enter the down payment date for purchase order"))

    def __str__(self):
        return _("Purchase Order #{id32}").format(id32=self.id32)

    @property
    def subtotal(self):
        amount = 0
        for item in self.purchaseorderitem_set.all():
            amount += item.subtotal
        return amount

    @property
    def subtotal_after_discount(self):
        return self.subtotal - self.discount_amount

    @property
    def total(self):
        return self.subtotal_after_discount + self.tax_amount - self.down_payment

    @property
    def margin(self):
        total = self.subtotal_after_discount
        amount = 0
        for item in self.purchaseorderitem_set.all():
            amount += item.margin
        return amount - total

    @property
    def magin_percent(self):
        try:
            return round(self.margin/self.subtotal_after_discount * 100, 2)
        except:
            return 0

    class Meta:
        ordering = ['-id']
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")


class PurchaseOrderItem(BaseModelGeneric):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        help_text=_("Select the purchase order associated with the item")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text=_("Select the product associated with the item")
    )
    quantity = models.PositiveIntegerField(
        help_text=_("Enter the item quantity")
    )
    po_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        help_text=_("Enter the purchase order item price")
    )
    actual_price = models.DecimalField(
        blank=True,
        null=True,
        max_digits=19,
        decimal_places=2,
        help_text=_("Enter the actual item price")
    )
    unit = models.ForeignKey(
        Unit, blank=True, null=True, on_delete=models.SET_NULL)

    # Add any other fields specific to your purchase order item model

    @property
    def subtotal(self):
        return self.po_price * self.quantity

    @property
    def margin(self):
        return self.subtotal - (self.quantity * self.product.base_price)

    def __str__(self):
        return _("Purchase Order Item #{id32} - {product}").format(id32=self.id32, product=self.product)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Purchase Order Item")
        verbose_name_plural = _("Purchase Order Items")


class InvalidPOItem(BaseModelGeneric):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        help_text=_("Select the purchase order associated with the item")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Select the product associated with the item")
    )
    price = models.DecimalField(
        blank=True,
        null=True,
        max_digits=19,
        decimal_places=2,
        help_text=_("Enter the item price")
    )
    discount = models.DecimalField(
        blank=True,
        null=True,
        max_digits=19,
        decimal_places=2,
        help_text=_("Enter the discount")
    )
    name = models.CharField(
        max_length=100,
        help_text=_("Enter the product name")
    )
    quantity = models.PositiveIntegerField(
        help_text=_("Enter the item quantity")
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True,
                             blank=True, help_text=_("Select the unit for the product"))

    class Meta:
        ordering = ['-id']
        verbose_name = _("Invalid Purchase Order Item")
        verbose_name_plural = _("Invalid Purchase Order Items")


class Shipment(BaseModelGeneric):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        help_text=_("Select the purchase order associated with the shipment")
    )
    shipment_date = models.DateField(
        help_text=_("Enter the shipment date")
    )
    # Add any other fields specific to your shipment model

    def __str__(self):
        return _("Shipment #{id32} - {purchase_order}").format(id32=self.id32, purchase_order=self.purchase_order)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Shipment")
        verbose_name_plural = _("Shipments")


class VendorPerformance(BaseModelGeneric):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        help_text=_(
            "Select the supplier associated with the vendor performance")
    )
    rating = models.PositiveIntegerField(
        choices=((1, _('Poor')), (2, _('Fair')), (3, _('Good')),
                 (4, _('Very Good')), (5, _('Excellent'))),
        help_text=_("Select the rating for the vendor performance")
    )
    comments = models.TextField(
        blank=True,
        help_text=_("Enter any comments or additional information")
    )
    # Add any other fields specific to vendor performance tracking

    def __str__(self):
        return _("Vendor Performance #{id32} - {supplier}").format(id32=self.id32, supplier=self.supplier)

    class Meta:
        ordering = ['-id']
        verbose_name = _("Vendor Performance")
        verbose_name_plural = _("Vendor Performances")


class PurchaseOrderPayment(BaseModelGeneric):
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

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        help_text=_('Select the invoice associated with the payment')
    )
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        help_text=_('Enter the payment amount')
    )
    payment_date = models.DateField(help_text=_('Enter the payment date'))
    payment_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_payment_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=255,  # Adjusting for the added descriptions
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text=_('Current status of the payment.')
    )

    def __str__(self):
        return _('Payment #{id32} - {po}').format(id32=self.id32, po=self.purchase_order)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')


class Payable(BaseModelGeneric):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='supplier_payables',
        help_text=_('Select the customer associated with the order')
    )
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='order_payables',
        related_query_name='orderitem',
        help_text=_('Select the order associated with the item')
    )
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='shipment_payables',
        help_text=_('Select the invoice associated with the payment')
    )
    payment = models.ForeignKey(
        PurchaseOrderPayment,
        on_delete=models.CASCADE,
        related_name='inbounds',
        blank=True,
        null=True,
        help_text=_('Select the invoice associated with the payment')
    )
    stock_movement = models.ForeignKey(
        StockMovement,
        on_delete=models.CASCADE,
        related_name='inbounds',
        blank=True,
        null=True,
        help_text=_('Select the invoice associated with the payment')
    )
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        help_text=_('Enter receivable amount')
    )
    paid_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_paid(self):
        return True if self.paid_at else None

    @property
    def less_30_days_amount(self):
        return self.order.less_30_days_amount

    @property
    def less_60_days_amount(self):
        return self.order.less_60_days_amount

    @property
    def less_90_days_amount(self):
        return self.order.less_90_days_amount

    @property
    def more_than_90_days_amount(self):
        return self.order.more_than_90_days_amount

    class Meta:
        ordering = ['-id']
        verbose_name = _('Payable')
        verbose_name_plural = _('Payables')
