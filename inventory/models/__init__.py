from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from libs.base_model import BaseModelGeneric, User

class Category(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the category name"))
    description = models.TextField(blank=True, help_text=_("Enter the category description"))

    def __str__(self):
        return f"Category #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Product(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the product name"))
    description = models.TextField(help_text=_("Enter the product description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Price in IDR (Rp)"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text=_("Select the product category"))
    quantity = models.IntegerField(help_text=_("Enter the product quantity"))

    def __str__(self):
        return f"Product #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    @property
    def phsycal_quantity(self):
        warehouse_stocks = WarehouseStock.objects.filter(product=self)
        total_quantity = warehouse_stocks.aggregate(models.Sum('quantity'))['quantity__sum']
        return total_quantity or 0


class ProductLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='logs', help_text=_("Select the product associated with the log"))
    quantity_change = models.IntegerField(help_text=_("Enter the quantity change"))
    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Specify the creation date"))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_updated_by", help_text=_("Select the user who created the log"))

    def __str__(self):
        return f"{self.product.name} - Quantity Change: {self.quantity_change}"

    class Meta:
        verbose_name = _("Product Log")
        verbose_name_plural = _("Product Logs")


class Warehouse(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the warehouse name"))
    address = models.TextField(help_text=_("Enter the warehouse address"))
    location = models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_("Enter the warehouse location coordinates")
    )

    def __str__(self):
        return f"Warehouse #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")


class WarehouseStock(BaseModelGeneric):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, help_text=_("Select the warehouse"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.IntegerField(default=0, help_text=_("Enter the product quantity in the warehouse"))

    def __str__(self):
        return f"Warehouse Stock: {self.warehouse.name} - Product: {self.product.name} - Quantity: {self.quantity}"

    class Meta:
        verbose_name = _("Warehouse Stock")
        verbose_name_plural = _("Warehouse Stocks")


class StockMovement(BaseModelGeneric):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.IntegerField(help_text=_("Enter the quantity"))
    from_warehouse_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='from_stockmovement_set',
        related_query_name='from_stockmovement',
        help_text=_("Select the content type of the source warehouse")
    )
    from_warehouse_id = models.PositiveIntegerField(blank=True, null=True, help_text=_("Enter the ID of the source warehouse"))
    from_warehouse = GenericForeignKey('from_warehouse_type', 'from_warehouse_id')
    to_warehouse_type = models.ForeignKey(
        ContentType,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='to_stockmovement_set',
        related_query_name='to_stockmovement',
        help_text=_("Select the content type of the destination warehouse")
    )
    to_warehouse_id = models.PositiveIntegerField(blank=True, null=True, help_text=_("Enter the ID of the destination warehouse"))
    to_warehouse = GenericForeignKey('to_warehouse_type', 'to_warehouse_id')
    movement_date = models.DateTimeField(blank=True, null=True, help_text=_("Specify the movement date"))

    def __str__(self):
        return f"Stock Movement #{self.id32}"

    class Meta:
        verbose_name = _("Stock Movement")
        verbose_name_plural = _("Stock Movements")

class StockAdjustment(BaseModelGeneric):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.IntegerField(help_text=_("Enter the quantity"))
    adjustment_date = models.DateField(help_text=_("Specify the adjustment date"))
    reason = models.TextField(blank=True, help_text=_("Enter the reason for the adjustment"))

    def __str__(self):
        return f"Stock Adjustment #{self.id32}"

    class Meta:
        verbose_name = _("Stock Adjustment")
        verbose_name_plural = _("Stock Adjustments")


class ReplenishmentOrder(BaseModelGeneric):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.PositiveIntegerField(help_text=_("Enter the quantity"))
    order_date = models.DateField(help_text=_("Specify the order date"))

    def __str__(self):
        return f"Replenishment Order #{self.id32}"

    class Meta:
        verbose_name = _("Replenishment Order")
        verbose_name_plural = _("Replenishment Orders")


class ReplenishmentReceived(BaseModelGeneric):
    replenishment_order = models.ForeignKey(ReplenishmentOrder, on_delete=models.CASCADE, help_text=_("Select the replenishment order"))
    received_date = models.DateField(help_text=_("Specify the received date"))

    def __str__(self):
        return f"Replenishment Received #{self.id32}"

    class Meta:
        verbose_name = _("Replenishment Received")
        verbose_name_plural = _("Replenishment Received")


@receiver(pre_save, sender=Product)
def calculate_product_log(sender, instance, **kwargs):
    previous_quantity = 0
    prev_obj = sender.objects.filter(pk=instance.pk).last()
    if prev_obj:
        previous_quantity = prev_obj.quantity
    instance.previous_quantity = previous_quantity


@receiver(post_save, sender=Product)
def create_product_log(sender, instance, **kwargs):
    quantity_change = instance.quantity - instance.previous_quantity
    ProductLog.objects.create(product=instance, quantity_change=quantity_change, created_by=instance.updated_by if instance.updated_by else instance.created_by)


@receiver(post_save, sender=StockMovement)
def update_warehouse_stock(sender, instance, **kwargs):
    # Deduct the quantity from the source warehouse
    if instance.from_warehouse_type == ContentType.objects.get_for_model(Warehouse):
        from_warehouse_stock, _ = WarehouseStock.objects.get_or_create(
            warehouse=instance.from_warehouse,
            product=instance.product,
            created_by=instance.created_by
        )
        from_warehouse_stock.quantity -= instance.quantity
        from_warehouse_stock.save()

    # Add the quantity to the destination warehouse
    if instance.to_warehouse_type == ContentType.objects.get_for_model(Warehouse):
        to_warehouse_stock, _ = WarehouseStock.objects.get_or_create(
            warehouse=instance.to_warehouse,
            product=instance.product,
            created_by=instance.created_by
        )
        to_warehouse_stock.quantity += instance.quantity
        to_warehouse_stock.save()
