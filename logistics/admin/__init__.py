from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from libs.admin import BaseAdmin
from inventory.models import StockMovement
from ..models import Vehicle, Driver, Job, DriverMovement


@admin.register(Vehicle)
class VehicleAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'driver']
    list_filter = ['driver']
    search_fields = ['name']
    fields = ['name', 'driver', 'license_plate']
    raw_id_fields = ['driver']


@admin.register(Driver)
class DriverAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'device_gps']
    search_fields = ['name']
    fields = ['name', 'phone_number', 'device_gps']


@admin.register(Job)
class JobAdmin(BaseAdmin):
    list_display = ['id32', 'vehicle', 'stock_movement', 'assigned_driver']
    list_filter = ['vehicle', 'assigned_driver']
    search_fields = ['vehicle__name', 'stock_movement__id32']
    fields = ['vehicle', 'stock_movement', 'assigned_driver', 'start_time', 'end_time']
    raw_id_fields = ['vehicle', 'assigned_driver']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "stock_movement":
            kwargs["queryset"] = StockMovement.objects.filter(
                origin_id__isnull=False,
                destination_id__isnull=False,
                status=4
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(DriverMovement)
class DriverMovementAdmin(gis_admin.OSMGeoAdmin, BaseAdmin):
    list_display = ['id32', 'driver', 'location', 'timestamp']
    list_filter = ['driver']
    search_fields = ['driver__name']
    fields = ['driver', 'location', 'timestamp']
