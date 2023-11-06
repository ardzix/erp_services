# signals.py (in the app where the Employee model is located)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models import Employee

@receiver(post_save, sender=User)
def create_employee_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Create an Employee instance for the new user
        Employee.objects.create(user=instance)
