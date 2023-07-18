# models.py in the "sales" app
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save, pre_delete
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from inventory.models import Product, StockMovement
from libs.base_model import BaseModelGeneric, User
from identities.models import CompanyProfile


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
        return f"Customer #{self.id32} - {self.name}"

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
        verbose_name=_("Approved by"),
        help_text=_("Select the user who approved the order")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved at"),
        help_text=_("Specify the date and time of approval")
    )
    # Add any other fields specific to your order model

    def __str__(self):
        return f"Order #{self.id32} - {self.customer}"

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderItem(BaseModelGeneric):
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
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
    # Add any other fields specific to your order item model

    def __str__(self):
        return f"Order Item #{self.id32} - {self.product}"

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
        verbose_name=_("Approved by"),
        help_text=_("Select the user who approved the invoice")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved at"),
        help_text=_("Specify the date and time of approval")
    )
    # Add any other fields specific to your invoice model

    def __str__(self):
        return f"Invoice #{self.id32} - {self.order}"

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
        verbose_name=_("Approved by"),
        help_text=_("Select the user who approved the payment")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved at"),
        help_text=_("Specify the date and time of approval")
    )
    # Add any other fields specific to your payment model

    def __str__(self):
        return f"Payment #{self.id32} - {self.invoice}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


@receiver(pre_save, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    if instance.pk:  # Only for existing OrderItem instances
        order_item = OrderItem.objects.get(pk=instance.pk)
        old_quantity = order_item.quantity
        quantity_diff = instance.quantity - old_quantity
        Product.objects.filter(pk=instance.product.pk).update(quantity=models.F(
            'quantity') - quantity_diff, updated_by_id=instance.updated_by_id)
        if quantity_diff < 0:
            StockMovement.objects.create(
                product_id=instance.product.pk,
                quantity=abs(quantity_diff),
                origin_type=ContentType.objects.get_for_model(
                    Customer),
                origin_id=order_item.order.customer.id,
                created_by=order_item.updated_by if order_item.updated_by else order_item.created_by
            )
        elif quantity_diff > 0:
            StockMovement.objects.create(
                product_id=instance.product.pk,
                quantity=abs(quantity_diff),
                destionation_type=ContentType.objects.get_for_model(
                    Customer),
                destionation_id=order_item.order.customer.id,
                created_by=order_item.updated_by if order_item.updated_by else order_item.created_by
            )


@receiver(pre_save, sender=SalesOrder)
def check_salesorder_before_approved(sender, instance, **kwargs):
    instance.approved_before = False
    so_before = SalesOrder.objects.filter(pk=instance.pk).last()
    if so_before:
        instance.approved_before = True if so_before.approved_at and so_before.approved_by else False


@receiver(post_save, sender=OrderItem)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity
        product.quantity -= quantity
        product.updated_by = instance.created_by
        product.save()


@receiver(post_save, sender=OrderItem)
def create_stock_movement(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity

        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            destionation_type=ContentType.objects.get_for_model(Customer),
            destionation_id=instance.order.customer.id,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )


@receiver(pre_delete, sender=OrderItem)
def restore_product_quantity(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.product.pk).update(
        quantity=models.F('quantity') + instance.quantity)
