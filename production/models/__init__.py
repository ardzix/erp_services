from django.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from inventory.models import Product, Unit, Warehouse
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
    item = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the component product"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Enter the quantity of the component in the BOM"))
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return _("Product #{id32} - {item} (BOM: {bom})").format(id32=self.id32, item=self.item, bom=self.bom)

    class Meta:
        verbose_name = _("BOM Product")
        verbose_name_plural = _("BOM Products")

class BOMComponent(BaseModelGeneric):
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, help_text=_("Select the associated BOM"))
    item = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the component product"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Enter the quantity of the component in the BOM"))
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return _("Component #{id32} - {item} (BOM: {bom})").format(id32=self.id32, item=self.item, bom=self.bom)

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
    work_order = models.ForeignKey(WorkOrder, blank=True, null=True, on_delete=models.SET_NULL, help_text=_("Select the associated work order"))
    work_center_warehouse = models.ForeignKey(Warehouse, blank=True, null=True, on_delete=models.CASCADE, help_text=_("Select the warehouse for the work center"))
    start_time = models.DateTimeField(blank=True, null=True, help_text=_("Enter the start time for production tracking"))
    end_time = models.DateTimeField(help_text=_("Enter the end time for production tracking"))
    products = models.ManyToManyField(Product, related_name='produced_items', through='ProducedItem', help_text=_("Select items produced from this Production"))
    components = models.ManyToManyField(Product, related_name='component_items', through='ComponentItem', help_text=_("Select materials used for this Production"))

    # Add any other fields specific to your production tracking modelb

    def __str__(self):
        return _("Production Tracking #{id32} - {work_order}").format(id32=self.id32, work_order=self.work_order)

    class Meta:
        verbose_name = _("Production Tracking")
        verbose_name_plural = _("Production Tracking")


class ProducedItem(BaseModelGeneric):
    production = models.ForeignKey(ProductionTracking, on_delete=models.CASCADE, help_text=_("Select the associated ProductionTracking"))
    item = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the produced item"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Enter the quantity of the component in the BOM"))
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    expire_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return _("Product #{id32} - {item} (Production: {production})").format(id32=self.id32, item=self.item, production=self.production)

    class Meta:
        verbose_name = _("Produced Item")
        verbose_name_plural = _("Produced Items")

class ComponentItem(BaseModelGeneric):
    production = models.ForeignKey(ProductionTracking, on_delete=models.CASCADE, help_text=_("Select the associated BOProductionTrackingM"))
    item = models.ForeignKey(Product, on_delete=models.CASCADE, help_text=_("Select the component item"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Enter the quantity of the component in the BOM"))
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return _("Component #{id32} - {item} (Production: {production})").format(id32=self.id32, item=self.item, production=self.production)

    class Meta:
        verbose_name = _("Component Item")
        verbose_name_plural = _("Component Items")