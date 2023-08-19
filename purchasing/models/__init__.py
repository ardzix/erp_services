from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from inventory.models import Product, StockMovement, Unit

class Supplier(BaseModelGeneric):
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
        on_delete=models.CASCADE,
        related_name='suppliers_profile',
        verbose_name=_("Company Profile"),
        help_text=_("Select the company profile for this supplier")
    )

    def __str__(self):
        return _("Supplier #{id32} - {name}").format(id32=self.id32, name=self.name)

    class Meta:
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
        help_text=_("Check if this supplier is the default supplier for the product")
    )

    def __str__(self):
        return _("{supplier} - {product}").format(supplier=self.supplier, product=self.product)

    class Meta:
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

    def __str__(self):
        return _("Purchase Order #{id32}").format(id32=self.id32)

    class Meta:
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
        max_digits=10,
        decimal_places=2,
        help_text=_("Enter the actual item price")
    )
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.SET_NULL)

    # Add any other fields specific to your purchase order item model

    def __str__(self):
        return _("Purchase Order Item #{id32} - {product}").format(id32=self.id32, product=self.product)

    class Meta:
        verbose_name = _("Purchase Order Item")
        verbose_name_plural = _("Purchase Order Items")

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
        verbose_name = _("Shipment")
        verbose_name_plural = _("Shipments")

class VendorPerformance(BaseModelGeneric):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        help_text=_("Select the supplier associated with the vendor performance")
    )
    rating = models.PositiveIntegerField(
        choices=((1, _('Poor')), (2, _('Fair')), (3, _('Good')), (4, _('Very Good')), (5, _('Excellent'))),
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
        verbose_name = _("Vendor Performance")
        verbose_name_plural = _("Vendor Performances")