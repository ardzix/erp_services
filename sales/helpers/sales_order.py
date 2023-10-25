from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement, StockMovementItem, Warehouse
from ..models import CustomerVisit, SalesOrder, Customer


def canvasing_create_stock_movement(instance, visit):
    """
    Handles the creation of StockMovement for SalesOrder instances that originate from canvasing.
    Sets the appropriate origin based on the associated customer visit and trip details.
    """
    sm = StockMovement.objects.create(
        destination_type=ContentType.objects.get_for_model(Customer),
        destination_id=instance.customer.id,
        creator_type=ContentType.objects.get_for_model(SalesOrder),
        creator_id=instance.id,
    )
    instance.stock_movement = sm

    visit = CustomerVisit.objects.filter(sales_order=instance).last()
    if visit and visit.trip and visit.trip.vehicle and visit.trip.vehicle.warehouse:
        sm.origin_type = ContentType.objects.get_for_model(Warehouse)
        sm.origin_id = visit.trip.vehicle.warehouse.id
        instance.type = visit.trip.type

    instance.save()
    sm.save()
    _create_stock_movement_items(instance)


def taking_order_create_stock_movement(instance):
    """
    Handles the creation of StockMovement for SalesOrder instances that originate from taking orders.
    Sets the appropriate origin based on the warehouse details associated with the SalesOrder.
    """
    sm = StockMovement.objects.create(
        origin_type=ContentType.objects.get_for_model(Warehouse),
        origin_id=instance.warehouse.id,
        creator_type=ContentType.objects.get_for_model(SalesOrder),
        creator_id=instance.id,
    )
    instance.stock_movement = sm
    instance.save()
    _create_stock_movement_items(instance)


def _create_stock_movement_items(instance):
    """
    Creates or updates StockMovementItem instances associated with a given SalesOrder instance.
    Each StockMovementItem corresponds to an item in the SalesOrder.
    """
    for item in instance.order_items.all():
        smi, created = StockMovementItem.objects.get_or_create(
            product_id=item.product.pk,
            stock_movement=instance.stock_movement
        )
        smi.quantity = item.quantity
        smi.unit = item.unit
        smi.save()


def handle_unapproved_sales_order(instance):
    """
    Deletes the StockMovement associated with an unapproved SalesOrder, 
    provided the status of the StockMovement is less than or equal to 4.
    """
    sm = instance.stock_movement
    if sm and sm.status <= 4:
        sm.delete()
