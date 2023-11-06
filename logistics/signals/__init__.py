from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from libs.constants import COMPLETED
from sales.models import Trip
from ..models import Job
from ..helpers import create_job_from_trip, create_drops_from_visits


@receiver(post_save, sender=Trip)
def create_job_on_canvasing(sender, instance, created, **kwargs):
    """
    Create a Job when a new Trip with type 'CANVASING' is created.
    """
    if created and instance.type == Trip.CANVASING:
        create_job_from_trip(instance)


@receiver(pre_save, sender=Trip)
def create_job_on_taking_order_complete(sender, instance, **kwargs):
    """
    Create a Job when a Trip with type 'TAKING_ORDER' changes status to 'COMPLETED'.
    """
    # Check if this is not a new instance
    if instance.pk:
        old_instance = Trip.objects.get(pk=instance.pk)
        if instance.type == Trip.TAKING_ORDER and instance.status == COMPLETED and old_instance.status != COMPLETED:
            create_job_from_trip(instance)

@receiver(post_save, sender=Job)
def generate_drops_for_job(sender, instance, created, **kwargs):
    """
    Generates Drop instances when a Job is created. Drops are generated based on the type of the trip.

    - For CANVASING trips, Drops are generated for each CustomerVisit.
    - For TAKING_ORDER trips, Drops are only generated for CustomerVisits with a COMPLETED status.
    """
    if created:  # Ensure Drops are only generated for newly created Jobs
        trip = instance.trip

        if trip.type == Trip.CANVASING:
            # Generate Drops for all CustomerVisits associated with the Trip
            customer_visits = trip.customervisit_set.all()
            create_drops_from_visits(instance, customer_visits)

        elif trip.type == Trip.TAKING_ORDER:
            # Generate Drops for CustomerVisits with a COMPLETED status
            completed_visits = trip.customervisit_set.filter(status=COMPLETED)
            create_drops_from_visits(instance, completed_visits)

