from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import StockMovement

@receiver(post_save, sender=StockMovement)
def on_invoice_created(sender, instance, created, **kwargs):
    if instance.status_before != instance.status and instance.status == StockMovement.DELIVERED and instance.purchase_order:
        supplier = instance.purchase_order.supplier
        Receivable.objects.get_or_create(
            customer=customer,
            order=instance.order,
            invoice=instance,
            amount=instance.amount
        )
        customer.has_receivable = True
        customer.save()