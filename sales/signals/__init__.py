from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement, Product, StockMovementItem, Warehouse
from ..models import OrderItem, SalesOrder, Customer


@receiver(pre_save, sender=OrderItem)
def update_unit(sender, instance, **kwargs):
    instance.unit = instance.product.sales_unit


@receiver(pre_save, sender=OrderItem)
def update_product_quantity(sender, instance, **kwargs):
    if instance.pk:  # Only for existing OrderItem instances
        order_item = OrderItem.objects.get(pk=instance.pk)
        old_quantity = order_item.quantity
        quantity_diff = instance.quantity - old_quantity
        sales_unit = instance.product.sales_unit
        stock_unit = instance.product.stock_unit
        quantity_diff = abs(quantity_diff) * sales_unit.conversion_to_top_level() / \
            stock_unit.conversion_to_top_level()
        Product.objects.filter(pk=instance.product.pk).update(quantity=models.F(
            'quantity') - quantity_diff, updated_by_id=instance.updated_by_id)
        if quantity_diff != 0 and instance.order.stock_movement:
            smi, created = StockMovementItem.objects.get_or_create(
                product_id=instance.product.pk,
                stock_movement=instance.order.stock_movement,
                created_by=order_item.created_by
            )
            smi.quantity = quantity_diff
            smi.unit = stock_unit
            smi.save()


@receiver(post_save, sender=OrderItem)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity * product.purchasing_unit.conversion_to_top_level()
        product.quantity -= quantity
        product.updated_by = instance.created_by
        product.save()


@receiver(pre_save, sender=SalesOrder)
def check_salesorder_before_approved(sender, instance, **kwargs):
    instance.approved_before = False
    instance.unapproved_before = False
    so_before = SalesOrder.objects.filter(pk=instance.pk).last()
    if so_before:
        instance.approved_before = True if so_before.approved_at and so_before.approved_by else False
        instance.unapproved_before = True if so_before.unapproved_at and so_before.unapproved_by else False


@receiver(post_save, sender=SalesOrder)
def create_stock_movement(sender, instance, **kwargs):
    if not instance.approved_before and instance.approved_at:
        sm = StockMovement.objects.create(
            destination_type=ContentType.objects.get_for_model(Customer),
            destination_id=instance.customer.id,
            created_by=instance.updated_by if instance.updated_by else instance.created_by
        )
        instance.stock_movement = sm
        instance.save()
        for item in OrderItem.objects.filter(order=instance).all():
            smi, created = StockMovementItem.objects.get_or_create(
                product_id=item.product.pk,
                stock_movement=instance.stock_movement,
                created_by=item.created_by
            )
            sales_unit = item.product.sales_unit
            stock_unit = item.product.stock_unit
            quantity = abs(item.quantity) * sales_unit.conversion_to_top_level() / \
                stock_unit.conversion_to_top_level()
            smi.quantity = quantity
            smi.unit = stock_unit
            smi.save()
    if not instance.unapproved_before and instance.unapproved_at:
        sm = instance.stock_movement
        if sm.status <= 4:
            sm.delete()


@receiver(post_save, sender=OrderItem)
def create_stock_movement_item(sender, instance, created, **kwargs):
    if created and instance.order.stock_movement:
        product = instance.product
        quantity = instance.quantity
        smi, created = StockMovementItem.objects.get_or_create(
            product=product,
            stock_movement=instance.order.stock_movement,
            created_by=instance.created_by
        )
        sales_unit = product.sales_unit
        stock_unit = product.stock_unit
        quantity = abs(quantity) * sales_unit.conversion_to_top_level() / \
            stock_unit.conversion_to_top_level()
        smi.quantity = quantity
        smi.unit = stock_unit
        smi.save()


@receiver(pre_delete, sender=OrderItem)
def restore_product_quantity(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.product.pk).update(
        quantity=models.F('quantity') + instance.quantity)
