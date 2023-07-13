from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from inventory.models import Product, StockMovement, Warehouse
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
    # Add any other fields specific to your work order model

    def __str__(self):
        return f"Work Order #{self.id32} - {self.production_order}"

    class Meta:
        verbose_name = _("Work Order")
        verbose_name_plural = _("Work Orders")


class ProductionTracking(BaseModelGeneric):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    produced_quantity = models.PositiveIntegerField()
    # Add any other fields specific to your production tracking model

    def __str__(self):
        return f"Production Tracking #{self.id32} - {self.work_order}"

    class Meta:
        verbose_name = _("Production Tracking")
        verbose_name_plural = _("Production Tracking")


@receiver(post_save, sender=WorkOrder)
def move_materials_to_workcenter(sender, instance, created, **kwargs):
    if created:
        # Fetch the BOM components for the associated product of the production order
        bom_components = BOMComponent.objects.filter(bom__product=instance.production_order.product)
        
        # Iterate over the BOM components and create stock movements to move materials from inventory to work center
        for component in bom_components:
            quantity = component.quantity * instance.production_order.quantity  # Calculate the required quantity based on the BOM and work order quantity
            product = component.component
            product.quantity -= quantity
            product.updated_by = instance.created_by
            product.save()
            StockMovement.objects.create(
                product=product,
                quantity=quantity,
                to_warehouse_type=ContentType.objects.get_for_model(Warehouse),
                to_warehouse_id=instance.work_center_warehouse.id,
                created_by=instance.created_by
            )


@receiver(pre_save, sender=WorkOrder)
def check_workorder_before_started(sender, instance, **kwargs):
    instance.started_before = False
    wo_before = WorkOrder.objects.filter(pk=instance.pk).last()
    if wo_before:
        instance.started_before = True if wo_before.start_date and wo_before.end_date else False

@receiver(post_save, sender=ProductionTracking)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.work_order.production_order.product
        quantity = instance.produced_quantity
        product.quantity += quantity
        product.updated_by = instance.created_by
        product.save()

@receiver(post_save, sender=ProductionTracking)
def create_stock_movement(sender, instance, created, **kwargs):
    if created:
        product = instance.work_order.production_order.product
        quantity = instance.produced_quantity

        StockMovement.objects.create(
            product=product,
            quantity=quantity,
            from_warehouse_type=ContentType.objects.get_for_model(Warehouse),
            from_warehouse_id=instance.work_order.work_center_warehouse.pk,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )

@receiver(pre_delete, sender=ProductionTracking)
def restore_product_quantity(sender, instance, **kwargs):
    product = instance.work_order.production_order.product
    quantity = instance.produced_quantity
    product.quantity -= quantity
    product.updated_by = instance.updated_by
    product.save()