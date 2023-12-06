# signals.py (in the app where the Employee model is located)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models import Employee, LocationTracker

@receiver(post_save, sender=User)
def create_employee_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Create an Employee instance for the new user
        Employee.objects.create(user=instance)



@receiver(post_save, sender=LocationTracker)
def update_employee_last_location(sender, instance, created, **kwargs):
    """
    Signal handler to update an employee's last location when a new LocationTracker instance is created.

    This handler is triggered after a LocationTracker instance is saved. If the instance is newly created,
    it updates the `last_location` field in the associated Employee model with the location from the
    LocationTracker instance.

    Parameters:
    - sender (Model Class): The model class that sent the signal. Should always be `LocationTracker`.
    - instance (LocationTracker): The instance of LocationTracker that was just saved.
    - created (bool): A boolean indicating whether this is a new instance or an update.
    - **kwargs: Additional keyword arguments. Not used in this handler but are standard for signal handlers.
    """
    if created:
        employee = instance.employee
        employee.last_location = instance.location
        employee.save()