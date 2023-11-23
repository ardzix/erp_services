import math
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.utils import timezone
from libs.constants import COMPLETED, SKIPPED
from inventory.models import StockMovement, StockMovementItem, Warehouse, Unit, WarehouseStock
from hr.models import Attendance
from ..models import CustomerVisit, SalesOrder, Customer, Trip


def canvasing_create_stock_movement(instance):
    """
    Creates StockMovement for SalesOrder instances that originate from canvasing.
    Sets the origin based on the associated customer visit and trip details.
    If this is the last visit, a stock movement for trip completion is triggered.

    Args:
        instance (SalesOrder): Instance of SalesOrder.
    """
    sm = initialize_stock_movement_for_canvasing(instance)
    set_stock_movement_origin_from_visit(sm, instance)
    finalize_stock_movement(sm)


def taking_order_create_stock_movement(instance):
    """
    Creates StockMovement for SalesOrder instances that originate from taking orders.
    Sets the origin and destination based on warehouse details associated with the SalesOrder.

    Args:
        instance (SalesOrder): Instance of SalesOrder.
    """
    trip = CustomerVisit.objects.filter(sales_order=instance).first().trip
    if not trip:
        return
    warehouse_content_type = ContentType.objects.get_for_model(Warehouse)
    sm = StockMovement.objects.create(
        origin_type=warehouse_content_type,
        origin_id=instance.warehouse.id,
        creator_type=ContentType.objects.get_for_model(SalesOrder),
        creator_id=instance.id,
    )
    set_stock_movement_destination_from_trip(sm, trip)
    instance.stock_movement = sm
    instance.save()
    sm.save()
    _create_stock_movement_items_from_sales_order(instance)


def initialize_stock_movement_for_canvasing(order_instance):
    """
    Initializes a StockMovement for canvasing.

    Args:
        order_instance (SalesOrder): Instance of SalesOrder.

    Returns:
        StockMovement: Created StockMovement instance.
    """
    sm = StockMovement.objects.create(
        destination_type=ContentType.objects.get_for_model(Customer),
        destination_id=order_instance.customer.id,
        creator_type=ContentType.objects.get_for_model(SalesOrder),
        creator_id=order_instance.id,
    )
    order_instance.stock_movement = sm
    return sm


def finalize_stock_movement(sm):
    """
    Finalizes the StockMovement instance by updating its status and movement date.

    :param sm: StockMovement instance that needs to be finalized.
    """
    sm.status = StockMovement.DELIVERED
    sm.movement_date = timezone.now()
    sm.save()


def set_stock_movement_origin_from_visit(sm, order_instance):
    """
    Sets origin for StockMovement based on customer visit and trip details.

    Args:
        sm (StockMovement): Instance of StockMovement.
        order_instance (SalesOrder): Instance of SalesOrder.
    """
    visit = CustomerVisit.objects.filter(sales_order=order_instance).last()
    if visit and visit.trip and visit.trip.vehicle and visit.trip.vehicle.warehouse:
        sm.origin_type = ContentType.objects.get_for_model(Warehouse)
        sm.origin_id = visit.trip.vehicle.warehouse.id
        order_instance.type = visit.trip.type
        order_instance.save()
        _create_stock_movement_items_from_sales_order(order_instance)


def set_stock_movement_destination_from_trip(sm, trip):
    """
    Sets the destination for StockMovement based on trip details.

    Args:
        sm (StockMovement): Instance of StockMovement.
        trip (Trip): Instance of Trip.
    """
    if trip and trip.vehicle and trip.vehicle.warehouse:
        sm.destination_type = ContentType.objects.get_for_model(Warehouse)
        sm.destination_id = trip.vehicle.warehouse.id


def _create_stock_movement_items_from_sales_order(instance):
    """
    Creates or updates StockMovementItem instances associated with a given SalesOrder instance.
    Each StockMovementItem corresponds to an item in the SalesOrder.
    """
    for item in instance.order_items.all():
        smi, created = StockMovementItem.objects.get_or_create(
            product_id=item.product.pk,
            stock_movement=instance.stock_movement,
            unit=item.unit
        )
        smi.quantity = item.quantity
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
    return old_status != COMPLETED and new_status == COMPLETED


def all_visits_completed_or_skipped(trip):
    """
    Checks if all associated CustomerVisits of a given trip are completed or skipped.
    :param trip: The Trip instance to check associated visits.
    :return: Boolean indicating if all visits are completed or skipped.
    """
    visits = CustomerVisit.objects.filter(trip=trip)
    total_visits = visits.count()
    completed_visits = visits.filter(
        status__in=[COMPLETED, SKIPPED]).count()

    return total_visits == completed_visits


def update_trip_status_to_completed(visit_instance):
    """
    Updates the status of the associated trip to completed.
    :param visit_instance: The CustomerVisit instance whose trip needs to be updated.
    """
    trip = visit_instance.trip
    trip.status = COMPLETED
    trip.updated_by = visit_instance.updated_by
    trip.save()


def handle_canvasing_trip(visit_instance):
    """
    Handles specific actions for CANVASING type trips.
    Updates the status of the previous stock movement associated with the trip to DELIVERED.
    :param visit_instance: The CustomerVisit instance with a CANVASING type trip.
    """
    trip = visit_instance.trip
    if trip.type == Trip.CANVASING:
        warehouse_type = ContentType.objects.get_for_model(Warehouse)
        prev_stock_movement = get_previous_stock_movement_destination(
            warehouse_type, trip.vehicle.warehouse.id).order_by('id').last()

        if prev_stock_movement:
            prev_stock_movement.status = StockMovement.DELIVERED
            prev_stock_movement.save()


def get_previous_stock_movement_destination(warehouse_type, warehouse_id):
    """
    Retrieves the previous stock movement based on warehouse type and ID.
    :param warehouse_type: ContentType of the Warehouse model.
    :param warehouse_id: ID of the warehouse.
    :return: QuerySet of matching StockMovement instances.
    """
    status_check = [StockMovement.DELIVERED,
                    StockMovement.ON_DELIVERY, StockMovement.READY]
    return StockMovement.objects.filter(
        destination_type=warehouse_type,
        destination_id=warehouse_id,
        status__in=status_check
    )


def set_salesperson_able_to_checkout(visit_instance):
    """
    Allows the salesperson associated with a trip to check out if all visits are done.
    :param visit_instance: The CustomerVisit instance whose trip's salesperson needs to be set able to checkout.
    """
    user = visit_instance.trip.salesperson
    attendance = Attendance.objects.filter(
        employee__user=user, clock_out__isnull=True).last()

    if attendance:
        attendance.able_checkout = True
        attendance.save()


def explode_stock_based_on_order_item(warehouse_stocks, item):
    """
    Check and manage stock levels for a specific order item.
    Explode stock recursively if necessary.

    Args:
    - warehouse_stocks (QuerySet): The queryset of WarehouseStock objects.
    - item (OrderItem): The order item to check stock against.
    """
    # Aggregate the total stock quantity for the given unit
    stocks = warehouse_stocks.filter(unit=item.unit).values(
        'product', 'unit').annotate(quantity=Sum('quantity'))
    stock_quantity = stocks[0]['quantity'] if stocks else 0

    # Explode stock if the quantity needed exceeds current stock
    if item.quantity > stock_quantity:
        explode_stock_recursively(item.quantity, item.unit, warehouse_stocks)


def explode_stock_recursively(quantity_needed, unit, warehouse_stocks):
    """
    Recursively explode stock to meet the required quantity.

    Args:
    - quantity_needed (int): The required quantity.
    - unit (Unit): The unit of measure for the required quantity.
    - warehouse_stocks (QuerySet): The queryset of WarehouseStock objects.
    """
    # Get child stocks one level deeper than the current unit
    child_stocks = warehouse_stocks.filter(
        quantity__gt=0, unit__level=unit.level + 1)

    # Aggregate the total quantity for child stocks
    stock_quantities = child_stocks.values(
        'product', 'unit').annotate(quantity=Sum('quantity'))

    # Get the immediate child unit of the current unit
    child_unit = Unit.objects.filter(parent=unit).first()
    if not child_unit:
        return  # Exit if no child unit found

    # Calculate the required quantity in terms of the child unit
    child_quantity_needed = math.ceil(
        quantity_needed / child_unit.conversion_to_ancestor(unit.id))
    available_quantity = stock_quantities[0]['quantity'] if stock_quantities else 0

    # Recursively explode stock if available quantity is insufficient
    if available_quantity < child_quantity_needed:
        explode_stock_recursively(
            child_quantity_needed - available_quantity, child_unit, warehouse_stocks)

    # Iterate through child stocks and explode as needed
    for stock in child_stocks:
        quantity_to_explode = min(child_quantity_needed, stock.quantity)
        commit_stock_explode(stock, quantity_to_explode)
        child_quantity_needed -= quantity_to_explode
        if child_quantity_needed <= 0:
            break  # Exit loop if needed quantity is met or exceeded


def commit_stock_explode(stock, quantity):
    """
    Commit the explosion of stock, adjusting quantities of parent and child stocks.

    Args:
    - stock (WarehouseStock): The stock to explode.
    - quantity (int): The quantity to explode.
    """
    # Get or create the parent stock for the current stock
    parent_stock, created = WarehouseStock.objects.get_or_create(
        warehouse=stock.warehouse,
        product=stock.product,
        unit=stock.unit.parent,
        expire_date=stock.expire_date
    )

    # Convert the quantity to parent unit and update the parent stock
    converted_quantity = quantity * \
        stock.unit.conversion_to_ancestor(stock.unit.parent.id)
    parent_stock.quantity += converted_quantity
    parent_stock.save()

    # Deduct the exploded quantity from the child stock
    stock.quantity -= quantity
    stock.save()
