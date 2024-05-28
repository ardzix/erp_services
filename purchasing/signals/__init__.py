
from math import prod
from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from inventory.models import StockMovement, Product, StockMovementItem, Warehouse, WarehouseStock
from inventory.serializers import warehouse
from purchasing.serializers import purchase_order
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


'''
@receiver(post_save, sender=WarehouseStock)
def create_auto_po(sender, instance, created, **kwargs):
    """
    Automatically creates a purchase order (PO) when a WarehouseStock instance is saved, based on the stock quantity 
    falling below the product's minimum quantity threshold. It considers the product's purchasing unit and supplier 
    preferences to generate the PO.

    Parameters:
    - sender: The model class that sent the signal.
    - instance: The actual instance being saved.
    - created: Boolean; True if a new record was created.
    - **kwargs: Keyword arguments.
    """
    product = instance.product
    warehouse_stocks = WarehouseStock.objects.filter(
        product=product,
        warehouse=instance.warehouse,
        quantity__gt=0)
    
    if not product.smallest_unit:
        return

    qty = 0
    for stock in warehouse_stocks:
        qty += stock.quantity * \
            stock.unit.conversion_to_ancestor(product.smallest_unit.id)

    if qty <= product.minimum_quantity * product.purchasing_unit.conversion_to_ancestor(product.smallest_unit.id):

        # Determine purchase quantity and supplier
        last_po_item = PurchaseOrderItem.objects.filter(
            product=product).order_by('-id').first()
        purchase_quantity = last_po_item.quantity if last_po_item else product.minimum_quantity
        supplier = get_supplier(product, last_po_item)

        if supplier:
            po = get_or_create_purchase_order(supplier, instance.warehouse)
            po_price = last_po_item.actual_price if last_po_item and last_po_item.actual_price else last_po_item.po_price if last_po_item else 0
            create_or_update_po_item(po, product, purchase_quantity, po_price)
'''


def get_supplier(product, last_po_item):
    """
    Determines the supplier for a new purchase order. It prioritizes the default supplier for the product, falls back 
    to the supplier of the last purchase order item for the product, and finally selects the most recent supplier for 
    the product if no default or last PO item supplier is available.

    Parameters:
    - product: The product instance to find a supplier for.
    - last_po_item: The last purchase order item instance for the product, if any.

    Returns:
    - The chosen supplier instance or None if no suitable supplier is found.
    """
    default_supplier = SupplierProduct.objects.filter(
        product=product, is_default_supplier=True).first()
    if default_supplier:
        return default_supplier.supplier
    if last_po_item:
        return last_po_item.purchase_order.supplier
    return SupplierProduct.objects.filter(product=product).last().supplier if SupplierProduct.objects.filter(product=product).exists() else None


def get_or_create_purchase_order(supplier, warehouse):
    """
    Retrieves an existing unapproved purchase order for the given supplier and warehouse or creates a new one if no 
    existing order matches the criteria.

    Parameters:
    - supplier: The supplier instance for the purchase order.
    - warehouse: The warehouse instance where the stock is kept.

    Returns:
    - A purchase order instance.
    """
    po = PurchaseOrder.objects.filter(
        approved_at__isnull=True,
        supplier=supplier,
        destination_warehouse=warehouse
    ).first()
    if not po:
        po = PurchaseOrder.objects.create(
            supplier=supplier,
            order_date=timezone.now(),
            destination_warehouse=warehouse,
        )
    return po


def create_or_update_po_item(purchase_order, product, quantity, price):
    """
    Creates a new purchase order item linked to a specific purchase order and product, or updates an existing item 
    if one already exists for the given purchase order and product. It sets the quantity and purchase price based on 
    the provided arguments.

    Parameters:
    - purchase_order: The purchase order instance the item belongs to.
    - product: The product instance for the purchase order item.
    - quantity: The quantity of the product to order.
    - price: The purchase price for the product.
    """
    po_item, created = PurchaseOrderItem.objects.get_or_create(
        purchase_order=purchase_order,
        product=product,
        defaults={'unit': product.purchasing_unit,
                  'quantity': quantity, 'po_price': price}
    )
    if not created:
        po_item.quantity += quantity  # Update quantity if PO item already exists
        po_item.po_price = price  # Update price if different
        po_item.save()
