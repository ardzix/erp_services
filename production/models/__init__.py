from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User

class Product(BaseModelGeneric):
    name = models.CharField(max_length=100)
    description = models.TextField()
    # Add any other fields specific to your product model

    def __str__(self):
        return f"Product #{self.id62} - {self.name}"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class BillOfMaterials(BaseModelGeneric):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    components = models.ManyToManyField(Product, related_name='used_in_bom', through='BOMComponent')

    def __str__(self):
        return f"BOM #{self.id62} - {self.product}"

    class Meta:
        verbose_name = _("Bill of Materials")
        verbose_name_plural = _("Bills of Materials")


class BOMComponent(BaseModelGeneric):
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE)
    component = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Component #{self.id62} - {self.component} (BOM: {self.bom})"

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
        return f"Production Order #{self.id62} - {self.product}"

    class Meta:
        verbose_name = _("Production Order")
        verbose_name_plural = _("Production Orders")


class WorkOrder(BaseModelGeneric):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE)
    operation_number = models.PositiveIntegerField()
    work_center = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders',
        verbose_name=_("Assigned to")
    )
    # Add any other fields specific to your work order model

    def __str__(self):
        return f"Work Order #{self.id62} - {self.production_order}"

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
        return f"Production Tracking #{self.id62} - {self.work_order}"

    class Meta:
        verbose_name = _("Production Tracking")
        verbose_name_plural = _("Production Tracking")
