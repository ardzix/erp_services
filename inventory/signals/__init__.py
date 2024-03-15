from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from hr.models import Attendance
from libs.constants import PICKER_CHECKER_GROUP_NAME
from ..models import Product, ProductLog, StockMovement, Warehouse, StockMovementItem, WarehouseStock
from ..helpers.stock_movement import handle_origin_warehouse, handle_destination_warehouse, is_dispatch_status_change


# Table of Content

# Pricing
# 1. commit_base_price: Commits a new base price for a product.
# 2. calculate_product_base_price: Computes the product's base price using fifo/lifo methodology.
# 3. calculate_product_sell_price: Calculates the product's sell price based on margin settings.

# Product log and stock
# 4. calculate_product_log: Gathers the product's previous details before saving.
# 5. create_product_log: Creates a log entry for product changes.
# 6. change_global_stock: Updates product quantity if its smallest unit changes.
# 7. create_dummy_warehouse_stock: Create dummy stock for all product units when new stock is created

# Stock Movement
# 8. check_sm_status_before: Logs the StockMovement's status before save.
# 9. check_movement_item_previous_status: Checks for status in movement item status before save.
# 10. handle_movement_item_status_change_post: Checks for changes in movement item status after save.
# 11. stock_movement_status_update: Updates stock movement status based on associated item's status.
# 12. set_movement_date_on_status_change: Set the movement_date to the current time if it's None

# Others
# 13. set_agent_able_to_checkout: Set agents (checker or picker) able to checkout if there is nothing to move


def commit_base_price(product, buy_price):
    """
    Commits a new base price for a product based on its purchasing unit and buy price.
    """
    if buy_price and product.purchasing_unit:
        base_price = buy_price / product.purchasing_unit.conversion_to_ancestor(product.purchasing_unit.id)
        if base_price != product.base_price:
            product.base_price = base_price
            product.save()


@receiver(post_save, sender=Product)
def change_global_stock(sender, instance, created, **kwargs):
    """
    Updates product quantity if there's a change in its smallest unit of measurement.
    """
    if not created and instance.previous_smallest_unit and instance.previous_smallest_unit != instance.smallest_unit:
        smallest_conversion = instance.previous_smallest_unit.conversion_to_top_level(
        ) / instance.smallest_unit.conversion_to_top_level()
        instance.quantity = instance.quantity * smallest_conversion
        instance.save()



@receiver(post_save, sender=Product)
def calculate_product_base_price(sender, instance, created, **kwargs):
    """
    Computes the product's base price using the specified methodology: highest, fifo, or lifo.
    """
    if not created:
        items = instance.get_purchase_item_history()[:2]  # Fetch the latest two items, if available

        # Function to handle 'highest' calculation method
        def highest_price():
            return items.aggregate(max_price=models.Max('buy_price'))['max_price'] if items else None

        # Mapping price calculation methods to their corresponding logic
        calculation_methods = {
            'highest': highest_price,
            'fifo': lambda: items[1].buy_price if len(items) == 2 else (items[0].buy_price if items else None),
            'lifo': lambda: items[0].buy_price if items else None,
        }

        # Get the calculation method from the instance
        calculation_method = calculation_methods.get(instance.price_calculation, lambda: None)
        
        # Calculate buy_price using the selected method
        buy_price = calculation_method()
        
        # If a buy_price was determined, update the instance's base price
        if buy_price:
            commit_base_price(instance, buy_price)


@receiver(post_save, sender=Product)
def calculate_product_sell_price(sender, instance, created, **kwargs):
    """
    Calculates the product's sell price based on the configured margin settings.
    """
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
    """
    Collects previous details of the product before it gets updated or saved.
    """
    prev_obj = sender.objects.filter(pk=instance.pk).last()
    instance.previous_quantity = prev_obj.quantity if prev_obj else 0
    instance._previous_buy_price = prev_obj.last_buy_price if prev_obj else 0
    instance.previous_base_price = prev_obj.base_price if prev_obj else 0
    instance.previous_sell_price = prev_obj.sell_price if prev_obj else 0
    instance.previous_smallest_unit = prev_obj.smallest_unit if prev_obj else None
    instance.previous_purchasing_unit = prev_obj.purchasing_unit if prev_obj else None


@receiver(post_save, sender=Product)
def create_product_log(sender, instance, **kwargs):
    """
    Creates a log entry whenever there's a change in product details such as quantity, buy price, base price, or sell price.
    """
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
    """
    Logs the StockMovement's current status before any change is made.
    """
    sm = StockMovement.objects.filter(pk=instance.pk).last()
    instance.status_before = sm.status if sm else 0


@receiver(post_save, sender=StockMovement)
def update_warehouse_stock(sender, instance, **kwargs):
    """
    Updates stocks in origin warehouses following changes in stock movement status of sales.
    """
    # need to fix this [temp]:
    if not instance.destination_type:
        return
    if instance.destination_type.model != 'customer':
        return
    if instance.origin_type == ContentType.objects.get_for_model(Warehouse) and is_dispatch_status_change(instance):
        for item in instance.items.all():
            handle_origin_warehouse(item)


@receiver(pre_save, sender=StockMovementItem)
def check_movement_item_previous_status(sender, instance, **kwargs):
    """
    Check status before saving the StockMovementItem, assign it to the instance to be used in post_save.
    """
    if not instance.pk:
        instance.origin_movement_status_before = StockMovementItem.WAITING
        instance.destination_movement_status_before = StockMovementItem.WAITING
    else:
        sm_prev = StockMovementItem.objects.get(id=instance.pk)
        instance.origin_movement_status_before = sm_prev.origin_movement_status
        instance.destination_movement_status_before = sm_prev.destination_movement_status


@receiver(post_save, sender=StockMovementItem)
def handle_movement_item_status_change_post(sender, instance, **kwargs):
    """
    Executes actions after saving the StockMovementItem, based on its origin movement status and its parent StockMovement's status.
    """
    stock_movement = instance.stock_movement
    # Condition 1: Set StockMovement status to PREPARING
    if instance.origin_movement_status == StockMovementItem.ON_PROGRESS and stock_movement.status != StockMovement.PREPARING:
        stock_movement.status = StockMovement.PREPARING
        stock_movement.save()

    # Condition 3: Set StockMovement status to VERIFYING
    all_items = stock_movement.items.all()
    if all(item.origin_movement_status == StockMovementItem.PUT for item in all_items):
        stock_movement.status = StockMovement.VERIFYING
        stock_movement.save()

    # Condition 3: Set StockMovement status to READY
    all_items = stock_movement.items.all()
    if all(item.origin_movement_status == StockMovementItem.CHECKED for item in all_items):
        stock_movement.status = StockMovement.READY
        stock_movement.save()

    # Condition 2: Set StockMovement status to ON_CHECK
    if instance.destination_movement_status == StockMovementItem.ON_CHECK and stock_movement.status != StockMovement.ON_CHECK:
        stock_movement.status = StockMovement.ON_CHECK
        stock_movement.save()

    # Condition 3: Set StockMovement status to CHECKED
    all_items = stock_movement.items.all()
    if all(item.destination_movement_status == StockMovementItem.CHECKED for item in all_items):
        stock_movement.status = StockMovement.CHECKED
        stock_movement.save()

    # Condition 3: Set StockMovement status to PUT
    all_items = stock_movement.items.all()
    if all(item.destination_movement_status == StockMovementItem.PUT for item in all_items):
        stock_movement.status = StockMovement.PUT
        stock_movement.movement_date = timezone.now()
        stock_movement.save()

    # Condition 4: Check for origin_movement_status change to CHECKED
    print(instance.origin_movement_status, instance.origin_checked_by)
    if instance.origin_movement_status == StockMovementItem.CHECKED and instance.origin_checked_by is None:
        instance._set_user_action(
            'approved', instance._current_user)
        instance._nullify_user_action('unapproved')
        instance.origin_checked_by = instance._current_user
        handle_origin_warehouse(instance)

    # Condition 5: Check for destination_movement_status change to CHECKED
    if instance.destination_movement_status == StockMovementItem.CHECKED and instance.destination_checked_by is None:
        instance._set_user_action(
            'approved', instance._current_user)
        instance._nullify_user_action('unapproved')
        instance.destination_checked_by = instance.approved_by

    # Condition 6: Check for destination_movement_status change to PUT
    if instance.destination_movement_status == StockMovementItem.PUT:
        instance._set_user_action(
            'published', instance._current_user)
        instance._nullify_user_action('unpublished')
        handle_destination_warehouse(instance)


@receiver(pre_save, sender=StockMovement)
def stock_movement_status_update(sender, instance, **kwargs):
    """
    Updates the StockMovement status to DELIVERED if all its associated items have a status set to FINISHED.
    """
    # Condition 3: If StockMovement is DELIVERED and all its items' origin_movement_status is set to FINISHED
    prev_obj = StockMovement.objects.filter(pk=instance.pk).last()
    if not prev_obj:
        return
    if prev_obj.status != StockMovement.DELIVERED and instance.status == StockMovement.DELIVERED:
        all_items = instance.items.all()
        all_items.update(origin_movement_status=StockMovementItem.FINISHED)


@receiver(post_save, sender=WarehouseStock)
def create_dummy_warehouse_stock(sender, instance, created, **kwargs):
    """
    Create dummy stock for all product units when new stock is created
    """
    if created:
        if not instance.product.units:
            return
        for unit in instance.product.units:
            if not WarehouseStock.objects.filter(product=instance.product, unit=unit).exists():
                WarehouseStock.objects.create(
                    warehouse=instance.warehouse,
                    product=instance.product,
                    expire_date=timezone.now(),
                    inbound_movement_item=instance.inbound_movement_item,
                    unit=unit
                )


@receiver(post_save, sender=StockMovement)
def set_agent_able_to_checkout(sender, instance, created, **kwargs):
    """
    After saving a StockMovement instance, this function checks if all stock movements
    for the current day are beyond certain stages. If so, it updates Attendance records to 
    allow agents (with roles such as picker or checker) to checkout.

    Args:
    - sender: The model class that sent the signal.
    - instance: The actual instance of StockMovement being saved.
    - created: Boolean, True if a new record was created.
    - kwargs: Additional keyword arguments.
    """
    # Only proceed if this is an update (not a creation)
    if created:
        return

    # Define the statuses representing stages before an agent can check out
    planning_statuses = [
        StockMovement.REQUESTED,
        StockMovement.PREPARING,
        StockMovement.VERIFYING,
        StockMovement.ON_CHECK,
        StockMovement.CHECKED,
    ]

    # Query today's movements
    today = timezone.localdate()
    today_movements = StockMovement.objects.filter(movement_date__date=today)

    # Check if all movements are beyond planning stages
    if today_movements.count() == today_movements.exclude(status__in=planning_statuses).count():
        # Collect warehouse IDs from today's movements
        warehouse_ids = set(today_movements.values_list('origin_id', flat=True)) | \
            set(today_movements.values_list('destination_id', flat=True))

        # Identify users associated with these warehouses who are part of picker/checker group
        users = User.objects.filter(
            id__in=Warehouse.objects.filter(
                id__in=warehouse_ids).values_list('pic', flat=True),
            groups__name__in=PICKER_CHECKER_GROUP_NAME
        )

        # Update Attendance records for these users
        Attendance.objects.filter(
            employee__user__in=users, clock_out__isnull=True
        ).update(able_checkout=True)


@receiver(pre_save, sender=StockMovement)
def set_movement_date_on_status_change(sender, instance, **kwargs):
    """
    Set the movement_date to the current time if it's None and status changes
    from REQUESTED to anything except CANCELED.
    """
    if instance.pk:
        # Fetch the previous state of the instance
        prev_instance = StockMovement.objects.get(pk=instance.pk)

        # Check if movement_date is None and status is changing as specified
        if instance.movement_date is None and prev_instance.status == StockMovement.REQUESTED and instance.status != StockMovement.CANCELED:
            # Set movement_date to current time
            instance.movement_date = timezone.now()