from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from inventory.models import Product, StockMovement, Unit
from libs.base_model import BaseModelGeneric, User
from identities.models import CompanyProfile

APPROVED_BY = "Approved by"
APPROVED_AT = "Approved at"
APPROVED_AT_HELP_TEXT = "Specify the date and time of approval"

class Customer(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("Enter the customer's name"))
    contact_number = models.CharField(
        max_length=15, help_text=_("Enter the contact number"))
    address = models.TextField(help_text=_("Enter the address"))
    location = models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_("Enter the location coordinates")
    )
    company_profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='customers_profile',
        verbose_name=_("Company Profile"),
        help_text=_("Select the company profile associated with the customer")
    )

    def __str__(self):
        return _("Customer #{id32} - {name}").format(id32=self.id32, name=self.name)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")


class SalesOrder(BaseModelGeneric):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        help_text=_("Select the customer associated with the order")
    )
    order_date = models.DateField(help_text=_("Enter the order date"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sales_orders',
        verbose_name=_(APPROVED_BY),
        help_text=_("Select the user who approved the order")
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

    def __str__(self):
        return _("Order #{id32} - {customer}").format(id32=self.id32, customer=self.customer)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderItem(BaseModelGeneric):
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='order_items',  # Update the related_name
        related_query_name='orderitem',
        help_text=_("Select the order associated with the item")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text=_("Select the product associated with the item")
    )
    quantity = models.PositiveIntegerField(
        help_text=_("Enter the item quantity"))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Enter the item price in IDR (Rp)")
    )
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)
    # Add any other fields specific to your order item model

    def __str__(self):
        return _("Order Item #{id32} - {product}").format(id32=self.id32, product=self.product)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")


class Invoice(BaseModelGeneric):
    order = models.OneToOneField(
        SalesOrder,
        on_delete=models.CASCADE,
        help_text=_("Select the order associated with the invoice")
    )
    invoice_date = models.DateField(help_text=_("Enter the invoice date"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sales_invoices',
        verbose_name=_(APPROVED_BY),
        help_text=_("Select the user who approved the invoice")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(APPROVED_AT),
        help_text=_(APPROVED_AT_HELP_TEXT)
    )
    # Add any other fields specific to your invoice model

    def __str__(self):
        return _("Invoice #{id32} - {order}").format(id32=self.id32, order=self.order)

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


class SalesPayment(BaseModelGeneric):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        help_text=_("Select the invoice associated with the payment")
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Enter the payment amount")
    )
    payment_date = models.DateField(help_text=_("Enter the payment date"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sales_payments',
        verbose_name=_(APPROVED_BY),
        help_text=_("Select the user who approved the payment")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_(APPROVED_AT),
        help_text=_(APPROVED_AT_HELP_TEXT)
    )
    # Add any other fields specific to your payment model

    def __str__(self):
        return _("Payment #{id32} - {invoice}").format(id32=self.id32, invoice=self.invoice)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")