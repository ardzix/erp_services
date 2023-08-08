from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from libs.base_model import BaseModelGeneric, User
from inventory.models import Product, StockMovement

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
        verbose_name=_("Company Profile")
    )

    def __str__(self):
        return f"Supplier #{self.id32} - {self.name}"

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
        return f"{self.supplier} - {self.product}"

    class Meta:
        verbose_name = _("Supplier Product")
        verbose_name_plural = _("Supplier Products")

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
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved at"),
    )
    # Add any other fields specific to your purchase order model

    def __str__(self):
        return f"Purchase Order #{self.id32}"

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
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Enter the item price in IDR (Rp)")
    )
    # Add any other fields specific to your purchase order item model

    def __str__(self):
        return f"Purchase Order Item #{self.id32} - {self.product}"

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
        return f"Shipment #{self.id32} - {self.purchase_order}"

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
        return f"Vendor Performance #{self.id32} - {self.supplier}"

    class Meta:
        verbose_name = _("Vendor Performance")
        verbose_name_plural = _("Vendor Performances")

@receiver(pre_save, sender=PurchaseOrderItem)
def update_product_quantity(sender, instance, **kwargs):
    if instance.pk:  # Only for existing PurchaseOrderItem instances
        purchase_order_item = PurchaseOrderItem.objects.get(pk=instance.pk)
        old_quantity = purchase_order_item.quantity
        quantity_diff = instance.quantity - old_quantity
        Product.objects.filter(pk=instance.product.pk).update(quantity=models.F(
            'quantity') + quantity_diff, updated_by_id=instance.updated_by_id)
        if quantity_diff > 0:
            StockMovement.objects.create(
                product_id=instance.product.pk,
                quantity=quantity_diff,
                origin_type=ContentType.objects.get_for_model(
                    Supplier),
                origin_id=instance.purchase_order.supplier.id,
                created_by=instance.updated_by if instance.updated_by else instance.created_by
            )
        elif quantity_diff < 0:
            StockMovement.objects.create(
                product_id=instance.product.pk,
                quantity=abs(quantity_diff),
                destination_type=ContentType.objects.get_for_model(
                    Supplier),
                destination_id=instance.purchase_order.supplier.id,
                created_by=instance.updated_by if instance.updated_by else instance.created_by
            )

@receiver(post_save, sender=PurchaseOrderItem)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity
        product.quantity += quantity
        product.updated_by = instance.created_by
        product.save()

@receiver(post_save, sender=PurchaseOrderItem)
def create_stock_movement(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity

        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            origin_type=ContentType.objects.get_for_model(Supplier),
            origin_id=instance.purchase_order.supplier.id,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )

@receiver(pre_delete, sender=PurchaseOrderItem)
def restore_product_quantity(sender, instance, **kwargs):
    product = instance.product
    old_quantity = instance.quantity
    product.quantity -= old_quantity
    product.updated_by = instance.updated_by
    product.save()
