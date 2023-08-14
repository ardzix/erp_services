from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from common.models import File
from identities.models import Brand


class Category(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("Enter the category name"))
    description = models.TextField(
        blank=True, help_text=_("Enter the category description"))

    def __str__(self):
        return _("Category #{category_id} - {category_name}").format(
            category_id=self.id32,
            category_name=self.name
        )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Unit(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the unit name"))
    symbol = models.CharField(
        max_length=10, help_text=_("Enter the unit symbol"))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='subunits', help_text=_("Select the parent unit"))
    conversion_factor = models.DecimalField(
        max_digits=10, decimal_places=4, default=1, help_text=_("Conversion factor to parent unit"))
    level = models.PositiveIntegerField(
        help_text=_("Unit depth level"), default=0)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

    def get_ancestors(self):
        """
        Returns a queryset of all parent units (ancestors) recursively.
        """
        ancestors = []
        current_unit = self.parent
        while current_unit is not None:
            ancestors.append(current_unit)
            current_unit = current_unit.parent
        return Unit.objects.filter(id__in=[ancestor.id for ancestor in ancestors])

    def get_descendants(self):
        """
        Returns a queryset of all child units (descendants) recursively.
        """
        descendants = []
        for child in self.subunits.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return Unit.objects.filter(id__in=[descendant.id for descendant in descendants])


class Product(BaseModelGeneric):
    PRODUCT_TYPE_CHOICES = [
        ('raw_material', _("Raw Material - Used to create other products")),
        ('finished_goods', _("Finished Goods - Completed and ready for sale")),
        ('intermediate', _("Intermediate Product - Partly finished, used in production")),
        ('consumable', _(
            "Consumable - Used in the production process but not part of the final product")),
    ]
    PRICE_CALCULATION = [
        ('fifo', _("FIFO - First in first out of buy price history")),
        ('lifo', _("LIFO - Last in first out of buy price history")),
        ('average', _("Average - Average of buy price history")),
        ('production_cost', _(
            "Production Cost - Form direct material cost, labour cost, and manufacturing overhead")),
    ]
    MARGIN_TYPE = [
        ('percentage', _("Percentage margin value from base price")),
        ('fixed', _("Fixed margin value")),
    ]

    name = models.CharField(
        max_length=100, help_text=_("Enter the product name"))
    alias = models.CharField(max_length=100, blank=True, null=True, help_text=_(
        "Enter the product alias name"))
    sku = models.CharField(max_length=100, help_text=_(
        "Enter the product stock keeping unit or barcode"))
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Enter the product description"))
    base_price = models.DecimalField(
        default=0,
        max_digits=10, decimal_places=2, help_text=_("Base price in IDR (Rp)"))
    last_buy_price = models.DecimalField(
        default=0,
        max_digits=10, decimal_places=2, help_text=_("Last buy price in IDR (Rp)"))
    sell_price = models.DecimalField(
        default=0,
        max_digits=10, decimal_places=2, help_text=_("Sell price in IDR (Rp)"))
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, help_text=_("Select the product category"))
    quantity = models.IntegerField(default=0, help_text=_("Enter the product quantity"))
    smallest_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, related_name='products_as_smallest',
                                      default=None, null=True, blank=True, help_text=_("Select the smallest unit for the product"))
    purchasing_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, related_name='products_as_purchasing',
                                        default=None, null=True, blank=True, help_text=_("Select the purchasing unit for the product"))
    sales_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, related_name='products_as_sales',
                                   default=None, null=True, blank=True, help_text=_("Select the sales unit for the product"))
    stock_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, related_name='products_as_stock',
                                   default=None, null=True, blank=True, help_text=_("Select the stock unit for the product"))
    product_type = models.CharField(
        max_length=20, choices=PRODUCT_TYPE_CHOICES, help_text=_("Select the product type"))
    price_calculation = models.CharField(max_length=20, choices=PRICE_CALCULATION, help_text=_(
        "Select on how the base price will be calculated"))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL,
                              null=True, blank=True, help_text=_("Select the product brand"))
    minimum_quantity = models.PositiveIntegerField(
        default=0,
        help_text=_(
            "Enter the minimum quantity at which the product needs to be restocked")
    )
    margin_type = models.CharField(max_length=20, choices=MARGIN_TYPE, help_text=_(
        "Select on how the margin will be calculated"))
    margin_value = models.DecimalField(
        default=0,
        max_digits=10, decimal_places=2,
        help_text=_(
            "Enter the value for margin (0-1 for percentage, >0 for fixed)")
    )
    is_active = models.BooleanField(
        default=False,
        help_text=_("Check if this product is active")
    )
    picture = models.ForeignKey(
        File, blank=True, null=True, on_delete=models.SET_NULL, help_text=_("Picture for the product"))

    def __str__(self):
        return _("Product #{product_id} - {product_name}").format(
            product_id=self.id32,
            product_name=self.name
        )

    def save(self, *args, **kwargs):
        if not self.purchasing_unit:
            self.purchasing_unit = self.smallest_unit
        if not self.sales_unit:
            self.sales_unit = self.smallest_unit
        if not self.stock_unit:
            self.stock_unit = self.smallest_unit
        super().save(*args, **kwargs)

    def get_purchase_item_history(self, exclude_zero_stock=True):
        stocks = WarehouseStock.objects.filter(product=self)
        if exclude_zero_stock:
            stocks = stocks.exclude(quantity=0)
        items = StockMovementItem.objects.filter(id__in=stocks.values_list('inbound_movement_item', flat=True)).order_by('-created_at')
        return items

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    @property
    def phsycal_quantity(self):
        warehouse_stocks = WarehouseStock.objects.filter(product=self)
        total_quantity = warehouse_stocks.aggregate(
            models.Sum('quantity'))['quantity__sum']
        return total_quantity or 0

    @property
    def previous_buy_price(self):
        buy_price_history = self.get_purchase_item_history(exclude_zero_stock=False).values('buy_price')
        return buy_price_history[1]['buy_price'] if buy_price_history.count()>1 else None

class ProductGroup(BaseModelGeneric):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='subgroups', help_text=_("Select the parent group"))
    name = models.CharField(
        max_length=100, help_text=_("Enter the product name"))
    products = models.ManyToManyField(Product)

    def __str__(self):
        return _("Product Group #{product_group_id} - {product_group_name}").format(
            product_group_id=self.id32,
            product_group_name=self.name
        )

    class Meta:
        verbose_name = _("Product Group")
        verbose_name_plural = _("Product Groups")


class ProductLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='logs', help_text=_(
        "Select the product associated with the log"))
    quantity_change = models.IntegerField(
        blank=True,
        null=True,
        help_text=_("Enter the quantity change"))
    buy_price_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Enter the buy price change"))
    base_price_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Enter the base price change"))
    sell_price_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Enter the base price change"))
    created_at = models.DateTimeField(
        auto_now_add=True, help_text=_("Specify the creation date"))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_updated_by", help_text=_(
        "Select the user who created the log"))

    def __str__(self):
        return _("{product_name} - Quantity Change: {quantity_change}").format(
            product_name=self.product.name,
            quantity_change=self.quantity_change
        )

    class Meta:
        verbose_name = _("Product Log")
        verbose_name_plural = _("Product Logs")


class Warehouse(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("Enter the warehouse name"))
    address = models.TextField(help_text=_("Enter the warehouse address"))
    location = models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_("Enter the warehouse location coordinates")
    )

    def __str__(self):
        return _("Warehouse #{warehouse_id} - {warehouse_name}").format(
            warehouse_id=self.id32,
            warehouse_name=self.name
        )

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")


class ProductLocation(BaseModelGeneric):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, help_text=_("Select the warehouse"))
    area = models.CharField(max_length=100, help_text=_(
        "Enter the area within the warehouse"))
    shelving = models.CharField(max_length=100, help_text=_(
        "Enter the shelving within the area"))
    position = models.CharField(max_length=100, help_text=_(
        "Enter the specific position on the shelving"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.PositiveIntegerField(default=0, help_text=_(
        "Enter the product quantity in this location"))

    def __str__(self):
        return _(
            "Warehouse: {warehouse_name} - Area: {area} - Shelving: {shelving} - "
            "Position: {position} - Product: {product_name} - Quantity: {quantity}"
        ).format(
            warehouse_name=self.warehouse.name,
            area=self.area,
            shelving=self.shelving,
            position=self.position,
            product_name=self.product.name,
            quantity=self.quantity
        )

    class Meta:
        verbose_name = _("Product Location")
        verbose_name_plural = _("Product Locations")


MOVEMENT_STATUS = (
    ('requested', _('Requested')),
    ('canceled', _('Canceled')),
    ('preparing', _('Preparing')),
    ('ready', _('Ready to pickup')),
    ('on_delivery', _('On Delivery')),
    ('delivered', _('Delivered')),
    ('returned', _('Returned')),
)


class StockMovement(BaseModelGeneric):
    origin_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='from_stockmovement_set',
        related_query_name='from_stockmovement',
        help_text=_("Select the content type of the source warehouse")
    )
    origin_id = models.PositiveIntegerField(
        blank=True, null=True, help_text=_("Enter the ID of the source warehouse"))
    origin = GenericForeignKey('origin_type', 'origin_id')
    destination_type = models.ForeignKey(
        ContentType,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='to_stockmovement_set',
        related_query_name='to_stockmovement',
        help_text=_("Select the content type of the destination warehouse")
    )
    destination_id = models.PositiveIntegerField(
        blank=True, null=True, help_text=_("Enter the ID of the destination warehouse"))
    destination = GenericForeignKey('destination_type', 'destination_id')
    movement_date = models.DateTimeField(
        blank=True, null=True, help_text=_("Specify the movement date"))
    status = models.CharField(max_length=20, choices=MOVEMENT_STATUS)

    def __str__(self):
        return _("Stock Movement #{movement_id}").format(movement_id=self.id32)

    class Meta:
        verbose_name = _("Stock Movement")
        verbose_name_plural = _("Stock Movements")


class StockMovementItem(BaseModelGeneric):
    stock_movement = models.ForeignKey(
        StockMovement,
        on_delete=models.CASCADE,
        related_name='items',
        help_text=_("Select the stock movement")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text=_("Select the product")
    )
    quantity = models.IntegerField(
        default=0, help_text=_("Enter the quantity"))
    buy_price = models.DecimalField(
        blank=True, null=True,
        max_digits=10, decimal_places=2, help_text=_("Buy price"))

    def __str__(self):
        return _("Stock Movement Item #{movement_item_id} - {product_name}").format(movement_item_id=self.id32, product_name=self.product)

    class Meta:
        verbose_name = _("Stock Movement Item")
        verbose_name_plural = _("Stock Movement Items")


class WarehouseStock(BaseModelGeneric):
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, help_text=_("Select the warehouse"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.PositiveIntegerField(default=0, help_text=_(
        "Enter the product quantity in the warehouse"))
    expire_date = models.DateField(blank=True, null=True)
    inbound_movement_item = models.ForeignKey(StockMovementItem, blank=True, null=True, on_delete=models.SET_NULL, related_name='inbound_stock_item')
    dispatch_movement_items = models.ManyToManyField(StockMovementItem, blank=True, related_name='dispatch_stock_items')

    def __str__(self):
        return _(
            "Warehouse Stock: {warehouse_name} - Product: {product_name} - Quantity: {quantity}"
        ).format(
            warehouse_name=self.warehouse.name,
            product_name=self.product.name,
            quantity=self.quantity
        )

    class Meta:
        verbose_name = _("Warehouse Stock")
        verbose_name_plural = _("Warehouse Stocks")


class StockAdjustment(BaseModelGeneric):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.IntegerField(help_text=_("Enter the quantity"))
    adjustment_date = models.DateField(
        help_text=_("Specify the adjustment date"))
    reason = models.TextField(blank=True, help_text=_(
        "Enter the reason for the adjustment"))

    def __str__(self):
        return _("Stock Adjustment #{adjustment_id}").format(adjustment_id=self.id32)

    class Meta:
        verbose_name = _("Stock Adjustment")
        verbose_name_plural = _("Stock Adjustments")


class ReplenishmentOrder(BaseModelGeneric):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, help_text=_("Select the product"))
    quantity = models.PositiveIntegerField(help_text=_("Enter the quantity"))
    order_date = models.DateField(help_text=_("Specify the order date"))

    def __str__(self):
        return _("Replenishment Order #{order_id}").format(order_id=self.id32)

    class Meta:
        verbose_name = _("Replenishment Order")
        verbose_name_plural = _("Replenishment Orders")


class ReplenishmentReceived(BaseModelGeneric):
    replenishment_order = models.ForeignKey(
        ReplenishmentOrder, on_delete=models.CASCADE, help_text=_("Select the replenishment order"))
    received_date = models.DateField(help_text=_("Specify the received date"))

    def __str__(self):
        return _("Replenishment Received #{order_received_id}").format(order_received_id=self.id32)

    class Meta:
        verbose_name = _("Replenishment Received")
        verbose_name_plural = _("Replenishment Received")
