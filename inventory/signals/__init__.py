from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from ..models import Product, ProductLog, StockMovement, WarehouseStock, Warehouse, StockMovementItem


def commit_base_price(product, buy_price):
    if buy_price and product.purchasing_unit and product.stock_unit:
        base_price = buy_price * product.stock_unit.conversion_to_top_level() / \
            product.purchasing_unit.conversion_to_top_level()
        if base_price != product.base_price:
            product.base_price = base_price
            product.save()


@receiver(post_save, sender=Product)
def change_global_stock(sender, instance, created, **kwargs):
    if not created:
        if instance.previous_smallest_unit and instance.previous_smallest_unit != instance.smallest_unit:
            smallest_conversion = instance.previous_smallest_unit.conversion_to_top_level() / instance.smallest_unit.conversion_to_top_level()
            instance.quantity = instance.quantity * smallest_conversion
            instance.save()
        if instance.previous_stock_unit and instance.previous_stock_unit != instance.stock_unit:
            stock_conversion = instance.previous_stock_unit.conversion_to_top_level() / instance.stock_unit.conversion_to_top_level()
            for stock in WarehouseStock.objects.filter(product=instance):
                stock.quantity = stock.quantity * stock_conversion
                stock.updated_by = instance.updated_by
                stock.save()


@receiver(post_save, sender=Product)
def calculate_product_base_price(sender, instance, created, **kwargs):
    if not created:
        items = instance.get_purchase_item_history()
        if instance.price_calculation in ['fifo', 'lifo']:
            buy_price = items.aggregate(
                max_price=models.Max('buy_price'))['max_price']
            commit_base_price(instance, buy_price)


@receiver(post_save, sender=Product)
def calculate_product_sell_price(sender, instance, created, **kwargs):
    if not created:
        if instance.margin_type == 'percentage':
            sell_price = instance.base_price * (instance.margin_value + 1)
        else:
            sell_price = instance.base_price + instance.margin_value
        if sell_price != instance.sell_price:
            instance.sell_price = sell_price
            instance.save()


@receiver(pre_save, sender=Product)
def calculate_product_log(sender, instance, **kwargs):
    prev_obj = sender.objects.filter(pk=instance.pk).last()
    instance.previous_quantity = prev_obj.quantity if prev_obj else 0
    instance._previous_buy_price = prev_obj.last_buy_price if prev_obj else 0
    instance.previous_base_price = prev_obj.base_price if prev_obj else 0
    instance.previous_sell_price = prev_obj.sell_price if prev_obj else 0
    instance.previous_smallest_unit = prev_obj.smallest_unit if prev_obj else None
    instance.previous_purchasing_unit = prev_obj.purchasing_unit if prev_obj else None
    instance.previous_sales_unit = prev_obj.sales_unit if prev_obj else None
    instance.previous_stock_unit = prev_obj.stock_unit if prev_obj else None


@receiver(post_save, sender=Product)
def create_product_log(sender, instance, **kwargs):
    quantity_change = instance.quantity - instance.previous_quantity
    buy_price_change = instance.last_buy_price - instance._previous_buy_price
    base_price_change = instance.base_price - instance.previous_base_price
    sell_price_change = instance.sell_price - instance.previous_sell_price
    if quantity_change != 0 or buy_price_change != 0 or base_price_change != 0 or sell_price_change != 0:
        ProductLog.objects.create(product=instance,
                                  quantity_change=quantity_change,
                                  buy_price_change=buy_price_change,
                                  base_price_change=base_price_change,
                                  sell_price_change=sell_price_change,
                                  created_by=instance.updated_by if instance.updated_by else instance.created_by)


@receiver(pre_save, sender=StockMovement)
def check_sm_status_before(sender, instance, **kwargs):
    sm = StockMovement.objects.filter(pk=instance.pk).last()
    instance.status_before = sm.status if sm else 0

# Deducts the stock quantity of a given `WarehouseStock` instance by the provided amount.
def deduct_stock(stock, quantity):
    stock.quantity -= quantity
    stock.save()

# Adds to the stock quantity of a given `WarehouseStock` instance by the provided amount.
def add_stock(stock, quantity):
    stock.quantity += quantity
    stock.save()

# Adjusts the last buy price of a product based on an item's buy price and its unit conversion.
def calculate_buy_price(item):
    product = item.product
    product.last_buy_price = item.buy_price / item.unit.conversion_to_top_level()
    product.save()

# Orders the `WarehouseStock` queryset based on the provided method: either 'lifo' or 'fifo'.
def filter_stock_by_method(stocks, method):
    order_field = '-created_at' if method == 'lifo' else 'created_at'
    return stocks.order_by(order_field)

# Handle items dispatch from a warehouse
# This will pick wich stocks to deduct when dispatch occurs
def handle_origin_warehouse(instance):
    for item in instance.items.all():
        if instance.status in ['on_delivery', 'delivered'] and instance.status_before not in ['on_delivery', 'delivered']:
            stocks = WarehouseStock.objects.filter(
                warehouse=instance.origin,
                product=item.product,
                quantity__gt=0
            )
            stocks = filter_stock_by_method(stocks, item.product.price_calculation)
            quantity_remaining = item.quantity
            for stock in stocks:
                stock.dispatch_movement_items.add(item)
                quantity = quantity_remaining if quantity_remaining <= stock.quantity else stock.quantity
                deduct_stock(stock, quantity)
                quantity_remaining -= quantity
                if quantity_remaining <=0:
                    continue

        # If the status is returned from delivered/delivery we need to put back the stocks
        elif instance.status not in ['on_delivery', 'delivered'] and instance.status_before in ['on_delivery', 'delivered']:
            stocks = WarehouseStock.objects.filter(
                warehouse=instance.origin,
                product=item.product,
                dispatch_movement_items=item)
            stocks = filter_stock_by_method(stocks, item.product.price_calculation)
            stock=stocks.first()
            stock.dispatch_movement_items.remove(item)
            add_stock(stock, item.quantity)


# Handle items inbound to a warehouse
# This will create stocks to inbound occurs
def handle_destination_warehouse(instance):
    for item in instance.items.all():
        stock, created = WarehouseStock.objects.get_or_create(
            warehouse=instance.destination,
            product=item.product,
            inbound_movement_item=item,
            created_by=instance.created_by,
            unit = item.unit,
            expire_date = item.expire_date
        )
        if instance.status == 'delivered' and instance.status_before != 'delivered':
            add_stock(stock, item.quantity)
            calculate_buy_price(item)
        elif instance.status != 'delivered' and instance.status_before == 'delivered':
            deduct_stock(stock, item.quantity)


@receiver(post_save, sender=StockMovement)
def update_warehouse_stock(sender, instance, **kwargs):
    if instance.origin_type == ContentType.objects.get_for_model(Warehouse):
        handle_origin_warehouse(instance)

    if instance.destination_type == ContentType.objects.get_for_model(Warehouse):
        handle_destination_warehouse(instance)

