from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from ..models import Product, ProductLog, StockMovement, WarehouseStock, Warehouse, StockMovementItem


def commit_base_price(product, base_price):
    if base_price and base_price != product.base_price:
        product.base_price = base_price
        product.save()

@receiver(post_save, sender=Product)
def calculate_product_base_price(sender, instance, created, **kwargs):
    if not created:
        items = instance.get_purchase_item_history()
        if instance.price_calculation in ['fifo', 'lifo']:
            base_price = items.aggregate(max_price=models.Max('buy_price'))['max_price']
            commit_base_price(instance, base_price)


@receiver(pre_save, sender=Product)
def calculate_product_log(sender, instance, **kwargs):
    previous_quantity = 0
    previous_buy_price = 0
    previous_base_price = 0
    previous_sell_price = 0
    prev_obj = sender.objects.filter(pk=instance.pk).last()
    if prev_obj:
        previous_quantity = prev_obj.quantity
        previous_buy_price = prev_obj.last_buy_price
        previous_base_price = prev_obj.base_price
        previous_sell_price = prev_obj.sell_price
    instance.previous_quantity = previous_quantity
    instance._previous_buy_price = previous_buy_price
    instance.previous_base_price = previous_base_price
    instance.previous_sell_price = previous_sell_price

@receiver(post_save, sender=Product)
def create_product_log(sender, instance, **kwargs):
    quantity_change = instance.quantity - instance.previous_quantity
    buy_price_change = instance.last_buy_price - instance._previous_buy_price
    base_price_change = instance.base_price - instance.previous_base_price
    sell_price_change = instance.sell_price - instance.previous_sell_price
    if quantity_change !=0 or buy_price_change !=0 or base_price_change !=0 or sell_price_change !=0:
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

def get_stock(stock_movement, item, get_from='destination'):
    imi = item if get_from=='destination' else None
    stock, created = WarehouseStock.objects.get_or_create(
        warehouse=stock_movement.destination if get_from == 'destination' else stock_movement.origin,
        product=item.product,
        inbound_movement_item=imi,
        created_by=stock_movement.created_by
    )
    if get_from=='origin':
        stock.dispatch_movement_items.add(item)
    return stock

def deduct_stock(stock, item):
    stock.quantity -= item.quantity
    stock.save()

def add_stock(stock, item):
    stock.quantity += item.quantity
    stock.save()

def calculate_buy_price(item):
    product = item.product
    product.last_buy_price = item.buy_price
    product.save()

@receiver(post_save, sender=StockMovement)
def update_warehouse_stock(sender, instance, **kwargs):
    # Deduct the quantity from the source warehouse
    if instance.origin_type == ContentType.objects.get_for_model(Warehouse):
        if instance.status == 5 and instance.status_before != 5:
            for item in instance.items.all():
                origin_stock = get_stock(instance, item, get_from='origin')
                deduct_stock(origin_stock, item)
        elif instance.status != 5 and instance.status_before == 5:
            for item in instance.items.all():
                origin_stock = get_stock(instance, item, get_from='origin')
                add_stock(origin_stock, item)

    # Add the quantity to the destination warehouse
    if instance.destination_type == ContentType.objects.get_for_model(Warehouse):
        if instance.status == 6 and instance.status_before != 6:
            for item in instance.items.all():
                destination_stock = get_stock(instance, item)
                add_stock(destination_stock, item)
                calculate_buy_price(item)
        if instance.status != 6 and instance.status_before == 6:
            for item in instance.items.all():
                destination_stock = get_stock(instance, item)
                deduct_stock(destination_stock, item)
