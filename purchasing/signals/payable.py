from datetime import timedelta
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement
from purchasing.serializers import purchase_order
from ..models import Payable, PurchaseOrderPayment, PurchaseOrder, PurchaseOrderItem, Supplier, Warehouse


@receiver(post_save, sender=StockMovement)
def on_sm_created(sender, instance, created, **kwargs):
    is_status_changed = instance.status_before != instance.status
    is_status_valid = instance.status == StockMovement.PUT
    is_origin_supplier = instance.origin_type == ContentType.objects.get_for_model(
        Supplier)
    is_destination_warehouse = instance.destination_type == ContentType.objects.get_for_model(
        Warehouse)

    if is_status_changed and is_status_valid and is_origin_supplier and is_destination_warehouse:
        # get billing_due_date
        order_date = instance.movement_date
        supplier = instance.origin
        billing_due_date = order_date + timedelta(days=supplier.payment_term)

        po = PurchaseOrder.objects.create(
            supplier=instance.origin,
            order_date=order_date,
            stock_movement=instance,
            destination_warehouse=instance.destination,
            billing_due_date=billing_due_date
        )

        items = instance.filter()
        for move_item in items:
            po_item = PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=move_item.product,
                quantity=move_item.quantity,
                po_price=move_item.buy_price,
                actual_price=move_item.buy_price,
                unit=move_item.unit,
            )
            move_item.po_item = po_item
            move_item.save()

        supplier = instance.purchase_order.supplier
        Payable.objects.get_or_create(
            supplier=supplier,
            order=po,
            stock_movement=instance,
            amount=instance.buy_price
        )
        supplier.has_payable = True
        supplier.save()


@receiver(pre_save, sender=PurchaseOrderPayment)
def create_next_trip_on_trip_complete(sender, instance, **kwargs):
    # Avoid processing for newly created instances
    if not instance.pk:
        return

    # Get the current status of the trip instance from the database
    status_before = PurchaseOrderPayment.objects.get(pk=instance.pk).status

    # Create a new trip if the current trip is transitioning to 'COMPLETED' or 'SKIPPED'
    if instance.status != status_before and instance.status == PurchaseOrderPayment.SETTLEMENT:
        payable = Payable.objects.get(invoice=instance.invoice)
        payable.payment = instance
        payable.paid_at = timezone.now()
        payable.save()

        supplier = payable.supplier
        if not supplier.payables.exists():
            supplier.has_payable = False
            supplier.save()


@receiver(pre_save, sender=StockMovement)
def check_po(sender, instance, **kwargs):
    prev_stock_movement = StockMovement.objects.filter(
        purchase_order=instance.purchase_order).first()
    if prev_stock_movement:
        instance.pk = prev_stock_movement.pk
        raise serializers.ValidationError({
            'purchase_order_id32': _("Stock movement with given purchase order is already exists.")
        })
