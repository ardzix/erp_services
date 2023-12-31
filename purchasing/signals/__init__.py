
from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement, Product, StockMovementItem, Warehouse
from ..models import SupplierProduct, PurchaseOrderItem, Supplier, PurchaseOrder


@receiver(pre_save, sender=SupplierProduct)
def ensure_single_default_supplier(sender, instance, **kwargs):
    # If the instance is set as default supplier:
    if instance.is_default_supplier:
        # Set all other instances where is_default_supplier is True for the same product to False:
        sender.objects.filter(product=instance.product, is_default_supplier=True)\
            .exclude(pk=instance.pk)\
            .update(is_default_supplier=False)

@receiver(pre_save, sender=PurchaseOrderItem)
def update_unit(sender, instance, **kwargs):
    instance.unit = instance.product.purchasing_unit

@receiver(pre_save, sender=PurchaseOrderItem)
def update_product_quantity(sender, instance, **kwargs):
    if instance.pk:  # Only for existing OrderItem instances
        order_item = PurchaseOrderItem.objects.get(pk=instance.pk)
        old_quantity = order_item.quantity
        quantity_diff = instance.quantity - old_quantity
        purchasing_unit = instance.product.purchasing_unit
        product_quantity = quantity_diff * purchasing_unit.conversion_to_top_level()
        Product.objects.filter(pk=instance.product.pk).update(quantity=models.F(
            'quantity') + product_quantity, updated_by_id=instance.updated_by_id)
        if quantity_diff != 0 and instance.purchase_order.stock_movement:
            item_price = instance.actual_price if instance.actual_price else instance.po_price
            item_price = item_price * purchasing_unit.conversion_to_top_level()
            smi, created = StockMovementItem.objects.get_or_create(
                product_id=instance.product.pk,
                stock_movement=instance.order.stock_movement,
                created_by=order_item.created_by
            )
            smi.buy_price = item_price
            smi.quantity = abs(quantity_diff)
            smi.unit = instance.product.purchasing_unit
            smi.save()


@receiver(post_save, sender=PurchaseOrderItem)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        quantity = instance.quantity * product.purchasing_unit.conversion_to_top_level()
        product.quantity += quantity
        product.updated_by = instance.created_by
        product.save()


@receiver(pre_save, sender=PurchaseOrder)
def check_purchaseorder_before_approved(sender, instance, **kwargs):
    instance.approved_before = False
    instance.unapproved_before = False
    po_before = PurchaseOrder.objects.filter(pk=instance.pk).last()
    if po_before:
        instance.approved_before = True if po_before.approved_at and po_before.approved_by else False
        instance.unapproved_before = True if po_before.unapproved_at and po_before.unapproved_by else False


@receiver(post_save, sender=PurchaseOrder)
def create_stock_movement(sender, instance, **kwargs):
    if not instance.approved_before and instance.approved_at:
        supplier_ct = ContentType.objects.get_for_model(Supplier)
        destination_ct = ContentType.objects.get_for_model(Warehouse) 
        sm = StockMovement.objects.create(
            origin_type=supplier_ct,
            origin_id=instance.supplier.id,
            destination_type=destination_ct if instance.destination_warehouse else None,
            destination_id=instance.destination_warehouse.id if instance.destination_warehouse else None,
        )
        instance.stock_movement = sm
        instance.save()
    if not instance.unapproved_before and instance.unapproved_at:
        sm = instance.stock_movement
        if sm.status not in ['on_delivery', 'delivered', 'returned']:
            sm.permanent_delete()


@receiver(post_save, sender=PurchaseOrderItem)
def create_stock_movement_item(sender, instance, created, **kwargs):
    if created and instance.purchase_order.stock_movement:
        product = instance.product
        quantity = instance.quantity
        purchasing_unit = product.purchasing_unit
        item_price = instance.actual_price if instance.actual_price else instance.po_price
        item_price = item_price * purchasing_unit.conversion_to_top_level()
        smi, created = StockMovementItem.objects.get_or_create(
            product=product,
            stock_movement=instance.purchase_order.stock_movement,
            created_by=instance.created_by
        )
        smi.buy_price = item_price
        smi.quantity = abs(quantity)
        smi.unit = instance.product.purchasing_unit
        smi.save()


@receiver(pre_delete, sender=PurchaseOrderItem)
def restore_product_quantity(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.product.pk).update(
        quantity=models.F('quantity') - instance.quantity)
