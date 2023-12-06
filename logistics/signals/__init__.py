from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.utils.translation import gettext_lazy as _
from libs.constants import COMPLETED, SKIPPED
from django.contrib.auth.models import User
from sales.models import Trip
from hr.models import Attendance
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


@receiver(post_save, sender=Job)
def set_able_checkout(sender, instance, **kwargs):
    """
    Signal handler that checks if all jobs assigned to a driver for the current day are either 'Skipped' or 'Completed'.

    This handler is triggered after a Job instance is saved. It verifies if the saved job's date is today. If so, it checks all of today's jobs for the same driver. If all of these jobs are marked as 'Skipped' or 'Completed', the 'able_to_checkout' method is called for the driver.

    Parameters:
    - sender (Model Class): The model class that sent the signal. Should always be `Job`.
    - instance (Job): The instance of the Job that was just saved.
    - **kwargs: Additional keyword arguments. Not used in this handler but are standard for signal handlers.
    """

    # Check if the updated job is for today
    if instance.date == timezone.localdate():
        driver = instance.assigned_driver

        # Check if all jobs for this driver today are either skipped or completed
        today_jobs = Job.objects.filter(assigned_driver=driver, date=timezone.localdate())
        if today_jobs.exclude(status__in=[SKIPPED, COMPLETED]).exists():
            return  # There are still jobs that are not skipped or completed

        # All jobs are either skipped or completed

        # Update Attendance records for these users
        Attendance.objects.filter(
            employee__user=driver.owned_by, clock_out__isnull=True
        ).update(able_checkout=True)