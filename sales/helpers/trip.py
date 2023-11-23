from libs.utils import add_one_day
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from inventory.models import StockMovement, StockMovementItem, Warehouse
from ..models import CustomerVisit, Trip
from ..models import Trip, CustomerVisit


def create_collector_trip(instance):
    """
    Helper function to create a collector trip.
    """
    trip_date = instance.date
    collector = instance.template.collector_pic.last()

    return Trip.objects.create(
        template = instance.template,
        date=add_one_day(add_one_day(trip_date)),  # Assumes add_one_day function exists
        salesperson=instance.salesperson,
        collector=collector,
        type=Trip.COLLECTING,
        parent=instance,
    )

def create_customer_visits_for_collector_trip(visits, trip):
    """
    Helper function to create customer visits for the new collector trip.
    """
    for visit in visits:
        CustomerVisit.objects.create(
            trip=trip,
            customer=visit.customer,
            sales_order=visit.sales_order,
            order=visit.order,
            item_delivery_evidence=visit.item_delivery_evidence
        )


def create_return_stock_movement(trip_instance):
    """Create inbound stock movement in the main warehouse when the trip is finished"""
    origin_warehouse = trip_instance.vehicle.warehouse if trip_instance.vehicle else None
    if not origin_warehouse:
        return

    warehouse_type = ContentType.objects.get_for_model(Warehouse)
    previous_stock_movement = get_previous_stock_movement_origin(
        warehouse_type, origin_warehouse.id)

    if not previous_stock_movement.exists():
        return

    destination_warehouse_id = previous_stock_movement.first().origin_id
    stock_movement = create_stock_movement(
        warehouse_type, origin_warehouse.id, destination_warehouse_id)

    _create_stock_movement_items_for_trip(
        stock_movement, origin_warehouse)


def get_previous_stock_movement_origin(warehouse_type, origin_warehouse_id):
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


def _create_stock_movement_items_for_trip(stock_movement, origin_warehouse):
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