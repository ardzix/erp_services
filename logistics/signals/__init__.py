from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from sales.models import Trip
from inventory.models import StockMovement, Warehouse
from ..models import Job


@receiver(post_save, sender=Trip)
def create_job_on_canvasing(sender, instance, created, **kwargs):
    """
    Create a Job when a new Trip with type 'CANVASING' is created.
    """
    if created and instance.type == Trip.CANVASING:
        Job.objects.create(vehicle=instance.vehicle, trip=instance, date=instance.date)


@receiver(pre_save, sender=Trip)
def create_job_on_taking_order_complete(sender, instance, **kwargs):
    """
    Create a Job when a Trip with type 'TAKING_ORDER' changes status to 'COMPLETED'.
    """
    # Check if this is not a new instance
    if instance.pk:
        old_instance = Trip.objects.get(pk=instance.pk)
        if instance.type == Trip.TAKING_ORDER and instance.status == Trip.COMPLETED and old_instance.status != Trip.COMPLETED:
            Job.objects.create(vehicle=instance.vehicle, trip=instance, date=instance.date)
