from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from libs.utils import get_config_value, TRUE
from sales.models import SalesOrder, Customer
from inventory.models import StockMovement, StockMovementItem, Warehouse

@receiver(post_save, sender=SalesOrder)
def deduct_stock_on_so_processing(sender, instance, **kwargs):
    """
    Deduct stock when sales order set to 'PROCESSING' if config says so
    """
    if instance.status == SalesOrder.PROCESSING and instance.so_before.status != instance.status and get_config_value('deduct_stock_on_sales_processing', 'false') in TRUE:
        sm = StockMovement.objects.create(
            origin_type = ContentType.objects.get_for_model(Warehouse),
            origin_id = instance.warehouse.id,
            destination_type = ContentType.objects.get_for_model(Customer),
            destination_id = instance.customer.id,
            movement_date = timezone.now(),
            status = StockMovement.DELIVERED
        )
        for item in instance.order_items.all():
            StockMovementItem.objects.create(
                stock_movement = sm,
                product = item.product,
                quantity = item.quantity,
                origin_movement_status = StockMovementItem.CHECKED,
                unit = item.unit
            )
