from django.contrib.contenttypes.models import ContentType
from purchasing.models import Supplier
from ..models import WarehouseStock


def deduct_stock(stock, quantity):
    """
    Deduct a specified quantity from a WarehouseStock instance.

    Args:
    - stock (WarehouseStock): The WarehouseStock instance to deduct from.
    - quantity (int/float): The amount to be deducted.

    """
    stock.quantity -= quantity
    stock.save()


def add_stock(stock, quantity):
    """
    Add a specified quantity to a WarehouseStock instance.

    Args:
    - stock (WarehouseStock): The WarehouseStock instance to add to.
    - quantity (int/float): The amount to be added.

    """
    stock.quantity += quantity
    stock.save()


def create_new_destination_stock(stock, item, quantity):
    """
    Create a new WarehouseStock instance for the destination warehouse.

    Args:
    - stock (WarehouseStock): The WarehouseStock instance to add to.
    - item (StockMovementItem): The StockMovementItem instance as reference.
    - quantity (int/float): The amount to be added.

    """
    WarehouseStock.objects.create(
        warehouse=item.stock_movement.destination,
        product=item.product,
        quantity=quantity,
        expire_date=stock.expire_date,
        inbound_movement_item=item,
        unit=item.unit
    )


def calculate_buy_price(item):
    """
    Recalculate the last buy price for a product based on a given item's buy price and unit conversion.

    Args:
    - item (Item): The StockMovementItem instance used to adjust the buy price.

    """
    product = item.product
    product.last_buy_price = (item.buy_price if item.buy_price else 0) / item.unit.conversion_to_top_level()
    product.save()


def filter_stock_by_method(stocks, method):
    """
    Sort a queryset of WarehouseStock based on a specified method: 'lifo' or 'fifo'.

    Args:
    - stocks (QuerySet): The WarehouseStock queryset to sort.
    - method (str): The method to use for sorting ('lifo' or 'fifo').

    Returns:
    - QuerySet: Sorted WarehouseStock queryset.
    """
    order_field = '-created_at' if method == 'lifo' else 'created_at'
    return stocks.order_by(order_field)


def is_dispatch_status_change(stock_movement):
    """
    Check if a given StockMovement has transitioned to 'on_delivery' or 'delivered' status.

    Args:
    - stock_movement (Instance): The StockMovement instance to check.

    Returns:
    - bool: True if the instance has transitioned, else False.
    """
    return stock_movement.status in ['on_delivery', 'delivered'] and stock_movement.status_before not in ['on_delivery', 'delivered']


def is_return_status_change(stock_movement):
    """
    Check if a given StockMovement instance has transitioned away from 'on_delivery' or 'delivered' status.

    Args:
    - stock_movement (Instance): The StockMovement instance to check.

    Returns:
    - bool: True if the instance has transitioned, else False.
    """
    return stock_movement.status not in ['on_delivery', 'delivered'] and stock_movement.status_before in ['on_delivery', 'delivered']


def handle_return_status_change(stock_movement, item):
    """
    Modify stock quantities based on the return status of an item.

    Args:
    - stock_movement (Instance): The StockMovement instance.
    - item (Item): The item whose stock needs adjusting.
    """
    stocks = get_filtered_stocks(
        stock_movement.origin, item, for_dispatch=False)
    stock = stocks.first()
    if stock:
        stock.dispatch_movement_items.remove(item)
        add_stock(stock, item.quantity)


def get_filtered_stocks(warehouse, item, for_dispatch=True):
    """
    Retrieve WarehouseStock based on specific filtering criteria.

    Args:
    - warehouse (Instance): The Warehouse instance to use for filtering.
    - item (Item): The item used for additional filtering.
    - for_dispatch (bool, optional): If True, filter for dispatch stocks. Default is True.

    Returns:
    - QuerySet: Filtered WarehouseStock queryset.
    """
    basic_filter = {
        'warehouse': warehouse,
        'product': item.product,
        'unit': item.unit
    }

    if for_dispatch:
        basic_filter['quantity__gt'] = 0
    else:
        basic_filter['dispatch_movement_items'] = item

    stocks = WarehouseStock.objects.filter(**basic_filter)
    return filter_stock_by_method(stocks, item.product.price_calculation)


def handle_destination_warehouse(item):
    """
    Manage inbound items to a warehouse, updating or creating stock records as needed.

    Args:
    - item (Instance): The inbound stock movement item.
    """
    stock_movement = item.stock_movement
    stock, created = WarehouseStock.objects.get_or_create(
        warehouse=item.stock_movement.destination,
        product=item.product,
        unit=item.unit,
        expire_date=item.expire_date
    )
    if not stock.inbound_movement_item:
        stock.inbound_movement_item = item
    add_stock(stock, item.quantity)
    if item.stock_movement.origin_type == ContentType.objects.get_for_model(Supplier):
        calculate_buy_price(item)

    if stock_movement.origin_type.model == 'warehouse':
        stocks = get_filtered_stocks(stock_movement.origin, item)
        quantity_remaining = item.quantity

        for stock in stocks:
            stock.dispatch_movement_items.add(item)
            quantity = quantity_remaining if quantity_remaining <= stock.quantity else stock.quantity
            deduct_stock(stock, quantity)
            quantity_remaining -= quantity
            if quantity_remaining <= 0:
                break


def handle_origin_warehouse(item):
    """
    Adjust stock quantities in the origin warehouse based on updates in stock movement status for associated items.

    Args:
    - item (Instance): The stock movement item instance.
    """
    stock_movement = item.stock_movement

    stocks = get_filtered_stocks(stock_movement.origin, item)

    quantity_remaining = item.quantity

    for stock in stocks:
        stock.dispatch_movement_items.add(item)
        quantity = quantity_remaining if quantity_remaining <= stock.quantity else stock.quantity
        deduct_stock(stock, quantity)
        if stock_movement.destination_type.model == 'warehouse':
            create_new_destination_stock(stock, item, quantity)
        quantity_remaining -= quantity
        if quantity_remaining <= 0:
            break
