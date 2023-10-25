from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric
from inventory.models import StockMovement, Warehouse


class Vehicle(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the vehicle name"))
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles', help_text=_("Select the driver for this vehicle"))
    license_plate = models.CharField(max_length=20, help_text=_("Enter the license plate"))
    warehouse = models.ForeignKey(Warehouse, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return _("Vehicle #{vehicle_id} - {vehicle_name} ({license_plate})").format(vehicle_id=self.id32, vehicle_name=self.name, license_plate=self.license_plate)

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")


class Driver(BaseModelGeneric):
    name = models.CharField(max_length=100, help_text=_("Enter the driver's name"))
    phone_number = models.CharField(max_length=15, help_text=_("Enter the driver's phone number"))
    device_gps = models.CharField(max_length=100, blank=True, null=True, help_text=_("Enter the device GPS information"))

    def __str__(self):
        return _("Driver #{driver_id} - {driver_name}").format(driver_id=self.id32, driver_name=self.name)

    class Meta:
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")


class Job(BaseModelGeneric):
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='jobs', help_text=_("Select the vehicle for this job"))
    trip = models.ForeignKey('sales.Trip', on_delete=models.CASCADE, related_name='jobs', help_text=_("Select the trip for this job"))
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs', help_text=_("Select the assigned driver for this job"))
    date = models.DateField(verbose_name=_(
        'Date'), help_text=_('Date for the job trip'))
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return _("Job #{job_id} - {trip}").format(job_id=self.id32, trip=self.trip)

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")


class DriverMovement(BaseModelGeneric):
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, related_name='movements', help_text=_("Select the driver for this movement"))
    location = gis_models.PointField(geography=True, null=True, blank=True, help_text=_("Enter the location coordinates"))
    timestamp = models.DateTimeField(auto_now_add=True, help_text=_("Specify the movement timestamp"))

    def __str__(self):
        return _("Driver Movement #{movement_id} - {driver_name} at {timestamp}").format(movement_id=self.id32, driver_name=self.driver, timestamp=self.timestamp)

    class Meta:
        verbose_name = _("Driver Movement")
        verbose_name_plural = _("Driver Movements")