from hashlib import blake2b
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from libs.base_model import BaseModelGeneric, User
from inventory.models import Product, StockMovement, Warehouse, WarehouseStock, StockMovementItem
from hr.models import Employee


class BillOfMaterials(BaseModelGeneric):
    name = models.CharField(max_length=150, blank=True, null=True, help_text=_("Name of this BoM"))
    products = models.ManyToManyField(Product, related_name='produced_from_bom', through='BOMProduct', help_text=_("Select items produced from this BOM"))
    components = models.ManyToManyField(Product, related_name='used_in_bom', through='BOMComponent', help_text=_("Select materials used for this BOM"))

    def __str__(self):
        return _("BOM #{id32} - {name}").format(id32=self.id32, name=self.name)

    class Meta:
        verbose_name = _("Bill of Materials")
        verbose_name_plural = _("Bills of Materials")


class BOMProduct(BaseModelGeneric):
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, help_text=_("Select the associated BOM"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the component product"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Enter the quantity of the component in the BOM"))

    def __str__(self):
        return _("Component #{id32} - {component} (BOM: {bom})").format(id32=self.id32, component=self.product, bom=self.bom)

    class Meta:
        verbose_name = _("BOM Product")
        verbose_name_plural = _("BOM Products")

class BOMComponent(BaseModelGeneric):
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, help_text=_("Select the associated BOM"))
    component = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the component product"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Enter the quantity of the component in the BOM"))

    def __str__(self):
        return _("Component #{id32} - {component} (BOM: {bom})").format(id32=self.id32, component=self.component, bom=self.bom)

    class Meta:
        verbose_name = _("BOM Component")
        verbose_name_plural = _("BOM Components")


class ProductionOrder(BaseModelGeneric):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the product for this production order"))
    quantity = models.PositiveIntegerField(help_text=_("Enter the quantity for the production order"))
    start_date = models.DateField(help_text=_("Enter the start date for the production order"))
    end_date = models.DateField(help_text=_("Enter the end date for the production order"))
    # Add any other fields specific to your production order model

    def __str__(self):
        return _("Production Order #{id32} - {product}").format(id32=self.id32, product=self.product)

    class Meta:
        verbose_name = _("Production Order")
        verbose_name_plural = _("Production Orders")


class WorkOrder(BaseModelGeneric):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, help_text=_("Select the associated production order"))
    operation_number = models.PositiveIntegerField(help_text=_("Enter the operation number for the work order"))
    work_center = models.CharField(max_length=100, help_text=_("Enter the work center for the work order"))
    work_center_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, help_text=_("Select the warehouse for the work center"))
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders',
        verbose_name=_("Assigned to"),
        help_text=_("Select the employee assigned to the work order")
    )
    start_time = models.DateTimeField(blank=True, null=True, help_text=_("Enter the start time for the work order"))
    end_time = models.DateTimeField(blank=True, null=True, help_text=_("Enter the end time for the work order"))
    # Add any other fields specific to your work order model

    def __str__(self):
        return _("Work Order #{id32} - {production_order}").format(id32=self.id32, production_order=self.production_order)

    class Meta:
        verbose_name = _("Work Order")
        verbose_name_plural = _("Work Orders")


class ProductionTracking(BaseModelGeneric):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, help_text=_("Select the associated work order"))
    start_time = models.DateTimeField(blank=True, null=True, help_text=_("Enter the start time for production tracking"))
    end_time = models.DateTimeField(help_text=_("Enter the end time for production tracking"))
    produced_quantity = models.PositiveIntegerField(help_text=_("Enter the quantity produced"))
    # Add any other fields specific to your production tracking model

    def __str__(self):
        return _("Production Tracking #{id32} - {work_order}").format(id32=self.id32, work_order=self.work_order)

    class Meta:
        verbose_name = _("Production Tracking")
        verbose_name_plural = _("Production Tracking")

@receiver(pre_save, sender=ProductionOrder)
def validate_production_order(sender, instance, **kwargs):
    product = instance.product

    # Check if the product has a BillOfMaterials
    bom_product = BOMProduct.objects.filter(product=product)
    bom = bom_product.first().bom
    if not bom:
        raise ValidationError({"product": _("Product must have a BillOfMaterials to create a ProductionOrder")})

    # Check if the product has any BOMComponent
    if not bom.components.exists():
        raise ValidationError({"product": _("Product must have at least one BOMComponent to create a ProductionOrder")})

def get_work_order_component_quantity(component, work_order):
    return component.quantity * work_order.production_order.quantity  # Calculate the required quantity based on the BOM and work order quantity

def get_stock(warehouse, component):
    try:
        return WarehouseStock.objects.get(warehouse=warehouse, product=component.component) 
    except WarehouseStock.DoesNotExist:
        raise ValidationError({"work_center_warehouse": _(f'Warehouse stock has not been set for this component (#{component.component})')})

@receiver(post_save, sender=WorkOrder)
def move_materials_to_workcenter(sender, instance, created, **kwargs):
    if created:
        # Fetch the BOM components for the associated product of the production order
        bom_product = BOMProduct.objects.filter(product=instance.production_order.product)
        bom = bom_product.first().bom
        bom_components = BOMComponent.objects.filter(bom=bom)
        
        # Iterate over the BOM components and deduct stocks
        for component in bom_components:
            quantity = get_work_order_component_quantity(component, instance)
            product = component.component
            product.quantity -= quantity
            product.updated_by = instance.created_by
            product.save()

            stock = get_stock(instance.work_center_warehouse, component)
            stock.quantity -= quantity
            stock.updated_by = instance.created_by
            stock.save()

@receiver(pre_save, sender=WorkOrder)
def check_workorder_before_started(sender, instance, **kwargs):
    if not instance.pk:
        product = instance.production_order.product
        warehouse = instance.work_center_warehouse
        bom_product = BOMProduct.objects.filter(product=product)
        bom = bom_product.first().bom
        bom_components = BOMComponent.objects.filter(bom=bom)
        # Iterate over the BOM components and check for stocks
        for component in bom_components:
            quantity = get_work_order_component_quantity(component, instance)
            stock = get_stock(warehouse, component)
            if stock.quantity < quantity:
                raise ValidationError({"product": _(f'Stock {component.component} is lower than quantity needed to produce {product}')})

@receiver(pre_save, sender=ProductionTracking)
def check_production_tracking(sender, instance, **kwargs):
    work_order = instance.work_order
    if not work_order.start_time:
        raise ValidationError({"work_order": _('Work order has not been started')})
    if work_order.end_time:
        raise ValidationError({"work_order": _('Work order has been finished')})

@receiver(pre_save, sender=ProductionTracking)
def set_tracking_time(sender, instance, **kwargs):
    instance.start_tim = instance.work_order.start_time

@receiver(post_save, sender=ProductionTracking)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.work_order.production_order.product
        quantity = instance.produced_quantity
        product.quantity += quantity
        product.updated_by = instance.created_by
        product.save()

        warehouse = instance.work_order.work_center_warehouse
        try:
            stock = WarehouseStock.objects.get(product=product, warehouse=warehouse)
        except WarehouseStock.DoesNotExist:
            raise ValidationError({"produced_quantity": _(f'Warehouse stock has not been set for this (#{product}) & (#{warehouse})')})
        stock.quantity += quantity
        stock.updated_by = instance.created_by
        stock.save()

@receiver(post_save, sender=ProductionTracking)
def update_work_order(sender, instance, created, **kwargs):
    if created:
        work_order = instance.work_order
        work_order.end_time = instance.end_time
        work_order.updated_by = instance.created_by
        work_order.save()

@receiver(post_save, sender=ProductionTracking)
def create_stock_movement(sender, instance, created, **kwargs):
    if created:
        product = instance.work_order.production_order.product
        quantity = instance.produced_quantity

        sm = StockMovement.objects.create(
            origin_type=ContentType.objects.get_for_model(Warehouse),
            origin_id=instance.work_order.work_center_warehouse.pk,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )

        StockMovementItem.objects.create(stock_movement=sm, product=product, quantity=quantity)

@receiver(pre_delete, sender=ProductionTracking)
def restore_product_quantity(sender, instance, **kwargs):
    product = instance.work_order.production_order.product
    quantity = instance.produced_quantity
    product.quantity -= quantity
    product.updated_by = instance.updated_by
    product.save()