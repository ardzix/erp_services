from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from sales.models import Invoice, SalesPayment, Receivable


@receiver(post_save, sender=Invoice)
def invoice_created(sender, instance, created, **kwargs):
    if created:
        customer = instance.order.customer
        Receivable.objects.get_or_create(
            customer=customer,
            order=instance.order,
            invoice=instance,
            amount=instance.amount
        )
        customer.has_receivable = True
        customer.save()

@receiver(pre_save, sender=SalesPayment)
def create_next_trip_on_trip_complete(sender, instance, **kwargs):
    # Avoid processing for newly created instances
    if not instance.pk:
        return

    # Get the current status of the trip instance from the database
    status_before = SalesPayment.objects.get(pk=instance.pk).status

    # Create a new trip if the current trip is transitioning to 'COMPLETED' or 'SKIPPED'
    if instance.status != status_before and instance.status == SalesPayment.SETTLEMENT:
        receivable = Receivable.objects.get(invoice=instance.invoice)
        receivable.payment = instance
        receivable.paid_at = timezone.now()
        receivable.save()

        customer = receivable.customer
        if not customer.receivables.exists():
            customer.has_receivable = False
            customer.save()
