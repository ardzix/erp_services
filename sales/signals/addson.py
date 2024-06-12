from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from libs.utils import get_config_value, TRUE
from sales.models import SalesOrder, Customer, OrderItem
from inventory.models import StockMovement, StockMovementItem, Warehouse, WarehouseStock

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


@receiver(post_save, sender=OrderItem)
def check_item_stock_before_create_sales_order(sender, instance, **kwargs):
    """
    Deduct stock when sales order set to 'PROCESSING' if config says so
    """
    if get_config_value('check_item_stock_before_create_sales_order', 'false') in TRUE:
        qty = 0
        for stock in WarehouseStock.objects.filter(product=instance.product, warehouse=instance.order.warehouse, quantity__gt=0):
            qty += stock.quantity * stock.unit.conversion_to_ancestor(instance.product.smallest_unit.id)
        
        if qty < instance.quantity * instance.unit.conversion_to_ancestor(instance.product.smallest_unit.id):
            raise ValidationError({'quantity': _('Item is out of stock.')})