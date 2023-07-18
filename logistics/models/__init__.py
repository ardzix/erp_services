from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric
from inventory.models import StockMovement


class Vehicle(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the vehicle name"))
    driver = models.ForeignKey(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles',
        help_text=_("Select the driver for this vehicle")
    )
    license_plate = models.CharField(max_length=20, help_text=_("Enter the license plate"))

    def __str__(self):
        return f"Vehicle #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

class Driver(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the driver's name"))
    phone_number = models.CharField(max_length=15, help_text=_("Enter the driver's phone number"))
    device_gps = models.CharField(max_length=100, blank=True, null=True, help_text=_("Enter the device GPS information"))

    def __str__(self):
        return f"Driver #{self.id32} - {self.name}"

    class Meta:
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")


class Job(BaseModelGeneric):
    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text=_("Select the vehicle for this job")
    )
    stock_movement = models.ForeignKey(
        StockMovement,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text=_("Select the stock movement for this job")
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_jobs',
        help_text=_("Select the assigned driver for this job")
    )
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Job #{self.id32} - {self.stock_movement}"

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")


class DriverMovement(BaseModelGeneric):
    driver = models.ForeignKey(
        'Driver',
        on_delete=models.CASCADE,
        related_name='movements',
        help_text=_("Select the driver for this movement")
    )
    location = gis_models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_("Enter the location coordinates")
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text=_("Specify the movement timestamp"))

    def __str__(self):
        return f"Driver Movement #{self.id32} - {self.driver} at {self.timestamp}"

    class Meta:
        verbose_name = _("Driver Movement")
        verbose_name_plural = _("Driver Movements")
