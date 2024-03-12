from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from libs.base_model import BaseModelGeneric, User
from libs.constants import (WAITING, ON_PROGRESS, ARRIVED, COMPLETED, SKIPPED)
from libs.filter import CreatedAtFilterMixin
from inventory.models import Warehouse
from common.models import File


STATUS_CHOICES = [
    (WAITING, _('Waiting')),
    (ON_PROGRESS, _('On Progress')),
    (ARRIVED, _('Arrived')),
    (COMPLETED, _('Completed')),
    (SKIPPED, _('Skipped'))
]


class Vehicle(BaseModelGeneric):
    name = models.CharField(
        max_length=100, help_text=_("Enter the vehicle name"))
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='vehicles', help_text=_("Select the driver for this vehicle"))
    license_plate = models.CharField(
        max_length=20, help_text=_("Enter the license plate"))
    warehouse = models.ForeignKey(
        Warehouse, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return _("Vehicle #{vehicle_id} - {vehicle_name} ({license_plate})").format(vehicle_id=self.id32, vehicle_name=self.name, license_plate=self.license_plate)

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")


class Driver(BaseModelGeneric):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, help_text=_(
        "The associated user of the driver"))
    name = models.CharField(
        max_length=100, help_text=_("Enter the driver's name"))
    phone_number = models.CharField(
        max_length=15, help_text=_("Enter the driver's phone number"))
    device_gps = models.CharField(max_length=100, blank=True, null=True, help_text=_(
        "Enter the device GPS information"))

    def __str__(self):
        return _("Driver #{driver_id} - {driver_name}").format(driver_id=self.id32, driver_name=self.name)

    class Meta:
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")


class Job(BaseModelGeneric):
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, help_text=_(
        "Select the vehicle for this job"))
    trip = models.ForeignKey('sales.Trip', on_delete=models.CASCADE, help_text=_(
        "Select the trip for this job"))
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='assigned_jobs', help_text=_("Select the assigned driver for this job"))
    date = models.DateField(verbose_name=_(
        'Date'), help_text=_('Date for the job trip'))
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=WAITING)

    def __str__(self):
        return _("Job #{job_id} - {trip}").format(job_id=self.id32, trip=self.trip)

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")


class Drop(BaseModelGeneric):
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='drops')
    location_name = models.CharField(
        max_length=100, help_text=_('Enter the location\'s name'))
    address = models.TextField(help_text=_('Enter the address'))
    location = models.PointField(
        geography=True,
        null=True,
        blank=True,
        help_text=_('Enter the location coordinates')
    )
    order = models.PositiveIntegerField(verbose_name=_(
        'Order'), help_text=_('Order of drop in the job'))
    travel_document = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_travel_document', blank=True, null=True, on_delete=models.SET_NULL)
    signature = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_signature', blank=True, null=True, on_delete=models.SET_NULL)
    visit_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_visit_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    item_delivery_evidence = models.ForeignKey(
        File, related_name='%(app_label)s_%(class)s_item_delivery_evidence', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=WAITING)
    retrieve_payment = models.BooleanField(default=False)
    sales_visit = models.ForeignKey(
        'sales.CustomerVisit', blank=True, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name = _('Drop')
        verbose_name_plural = _('Drops')

    def __str__(self):
        return f'{self.job} - {self.location_name}'

    @property
    def sales_order(self):
        return self.sales_visit.sales_order if self.sales_visit else None

    @property
    def items(self):
        return self.sales_visit.sales_order.order_items.all() if self.sales_visit and self.sales_visit.sales_order else []