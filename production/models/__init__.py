from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from libs.base_model import BaseModelGeneric, User
from inventory.models import Product, StockMovement, Warehouse, WarehouseStock
from hr.models import Employee


class BillOfMaterials(BaseModelGeneric):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    components = models.ManyToManyField(Product, related_name='used_in_bom', through='BOMComponent')

    def __str__(self):
        return f"BOM #{self.id32} - {self.product}"

    class Meta:
        verbose_name = _("Bill of Materials")
        verbose_name_plural = _("Bills of Materials")


class BOMComponent(BaseModelGeneric):
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE)
    component = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Component #{self.id32} - {self.component} (BOM: {self.bom})"

    class Meta:
        verbose_name = _("BOM Component")
        verbose_name_plural = _("BOM Components")


class ProductionOrder(BaseModelGeneric):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    # Add any other fields specific to your production order model

    def __str__(self):
        return f"Production Order #{self.id32} - {self.product}"

    class Meta:
        verbose_name = _("Production Order")
        verbose_name_plural = _("Production Orders")


class WorkOrder(BaseModelGeneric):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE)
    operation_number = models.PositiveIntegerField()
    work_center = models.CharField(max_length=100)
    work_center_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders',
        verbose_name=_("Assigned to")
    )
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    # Add any other fields specific to your work order model

    def __str__(self):
        return f"Work Order #{self.id32} - {self.production_order}"

    class Meta:
        verbose_name = _("Work Order")
        verbose_name_plural = _("Work Orders")


class ProductionTracking(BaseModelGeneric):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    produced_quantity = models.PositiveIntegerField()
    # Add any other fields specific to your production tracking model

    def __str__(self):
        return f"Production Tracking #{self.id32} - {self.work_order}"

    class Meta:
        verbose_name = _("Production Tracking")
        verbose_name_plural = _("Production Tracking")

@receiver(pre_save, sender=ProductionOrder)
def validate_production_order(sender, instance, **kwargs):
    product = instance.product

    # Check if the product has a BillOfMaterials
    try:
        bom = product.billofmaterials
    except BillOfMaterials.DoesNotExist:
        raise ValidationError("Product must have a BillOfMaterials to create a ProductionOrder")

    # Check if the product has any BOMComponent
    if not bom.components.exists():
        raise ValidationError("Product must have at least one BOMComponent to create a ProductionOrder")

def get_work_order_component_quantity(component, work_order):
    return component.quantity * work_order.production_order.quantity  # Calculate the required quantity based on the BOM and work order quantity

def get_stock(warehouse, component):
    return WarehouseStock.objects.get(warehouse=warehouse, product=component.component)

@receiver(post_save, sender=WorkOrder)
def move_materials_to_workcenter(sender, instance, created, **kwargs):
    if created:
        # Fetch the BOM components for the associated product of the production order
        bom_components = BOMComponent.objects.filter(bom__product=instance.production_order.product)
        
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
        bom_components = BOMComponent.objects.filter(bom__product=product)
        # Iterate over the BOM components and check for stocks
        for component in bom_components:
            quantity = get_work_order_component_quantity(component, instance)
            stock = get_stock(warehouse, component)
            if stock.quantity < quantity:
                raise ValidationError(_(f'Stock {component.component} is lower than quantity needed to produce {product}'))

@receiver(pre_save, sender=ProductionTracking)
def check_production_tracking(sender, instance, **kwargs):
    work_order = instance.work_order
    if not work_order.start_time:
        raise ValidationError(_('Work order has not been started'))
    if work_order.end_time:
        raise ValidationError(_('Work order has been finished'))

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
        stock = WarehouseStock.objects.get(product=product, warehouse=warehouse)
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

        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            origin_type=ContentType.objects.get_for_model(Warehouse),
            origin_id=instance.work_order.work_center_warehouse.pk,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )

@receiver(pre_delete, sender=ProductionTracking)
def restore_product_quantity(sender, instance, **kwargs):
    product = instance.work_order.production_order.product
    quantity = instance.produced_quantity
    product.quantity -= quantity
    product.updated_by = instance.updated_by
    product.save()