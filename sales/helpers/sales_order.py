from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from inventory.models import StockMovement, StockMovementItem, Warehouse
from ..models import CustomerVisit, SalesOrder, Customer, Trip


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
    _create_stock_movement_items_from_sales_order(instance)


def taking_order_create_stock_movement(instance):
    """
    Handles the creation of StockMovement for SalesOrder instances that originate from taking orders.
    Sets the appropriate origin based on the warehouse details associated with the SalesOrder.
    """
    trip = CustomerVisit.objects.filter(sales_order=instance).first().trip
    warehouse_content_type = ContentType.objects.get_for_model(Warehouse)
    sm = StockMovement.objects.create(
        origin_type=warehouse_content_type,
        origin_id=instance.warehouse.id,
        creator_type=ContentType.objects.get_for_model(SalesOrder),
        creator_id=instance.id,
    )
    if trip and trip.vehicle and trip.vehicle.warehouse:
        sm.destination_type = warehouse_content_type
        sm.destination_id = trip.vehicle.warehouse.id
    instance.stock_movement = sm
    instance.save()
    sm.save()
    _create_stock_movement_items_from_sales_order(instance)


def _create_stock_movement_items_from_sales_order(instance):
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


def has_completed_status_changed(old_status, new_status):
    """Check if the status has changed from non-completed to completed."""
    return old_status != Trip.COMPLETED and new_status == Trip.COMPLETED


def create_stock_movement_for_trip(trip_instance):
    """Create stock movement based on trip instance."""
    origin_warehouse = trip_instance.vehicle.warehouse if trip_instance.vehicle else None
    if not origin_warehouse:
        return

    warehouse_type = ContentType.objects.get_for_model(Warehouse)
    previous_stock_movement = get_previous_stock_movement(
        warehouse_type, origin_warehouse.id)

    if not previous_stock_movement.exists():
        return

    destination_warehouse_id = previous_stock_movement.first().origin_id
    stock_movement = create_stock_movement(
        warehouse_type, origin_warehouse.id, destination_warehouse_id)

    _create_stock_movement_items_for_trip_trip(stock_movement, origin_warehouse)


def get_previous_stock_movement(warehouse_type, origin_warehouse_id):
    """Retrieve previous stock movement based on warehouse type and origin."""
    status_check = [StockMovement.DELIVERED,
                    StockMovement.ON_DELIVERY, StockMovement.READY]
    return StockMovement.objects.filter(
        destination_type=warehouse_type,
        destination_id=origin_warehouse_id,
        status__in=status_check
    )


def create_stock_movement(warehouse_type, origin_id, destination_id):
    """Create and return a new stock movement."""
    return StockMovement.objects.create(
        origin_type=warehouse_type,
        origin_id=origin_id,
        destination_type=warehouse_type,
        destination_id=destination_id,
        movement_date=timezone.now()
    )


def _create_stock_movement_items_for_trip_trip(stock_movement, origin_warehouse):
    """Create stock movement items for products with quantity greater than zero in origin warehouse."""
    stocks = origin_warehouse.warehousestock_set.filter(
        quantity__gt=0
    ).values('product', 'unit').annotate(total_quantity=Sum('quantity'))

    for stock in stocks:
        StockMovementItem.objects.create(
            product_id=stock.get('product'),
            stock_movement=stock_movement,
            unit_id=stock.get('unit'),
            quantity=stock.get('total_quantity')
        )
