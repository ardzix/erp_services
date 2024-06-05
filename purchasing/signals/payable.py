from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework import serializers
from django.utils import timezone
from inventory.models import StockMovement
from django.utils.translation import gettext_lazy as _
from purchasing.serializers import purchase_order
from ..models import Payable, PurchaseOrderPayment


@receiver(post_save, sender=StockMovement)
def on_sm_created(sender, instance, created, **kwargs):
    if instance.status_before != instance.status and instance.status in [StockMovement.DELIVERED, StockMovement.PUT] and instance.purchase_order:
        supplier = instance.purchase_order.supplier
        Payable.objects.get_or_create(
            supplier=supplier,
            order=instance.purchase_order,
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
    prev_stock_movement = StockMovement.objects.filter(purchase_order=instance.purchase_order).first()
    if prev_stock_movement and instance.purchase_order:
        instance.pk = prev_stock_movement.pk
        raise serializers.ValidationError({
            'purchase_order_id32': _("Stock movement with given purchase order is already exists.")
        })
