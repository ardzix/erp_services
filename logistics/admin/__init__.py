from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from libs.admin import BaseAdmin
from inventory.models import StockMovement
from ..models import Vehicle, Driver, Job, Drop


@admin.register(Vehicle)
class VehicleAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'driver']
    list_filter = ['driver']
    search_fields = ['name']
    fields = ['name', 'driver', 'license_plate', 'warehouse']
    raw_id_fields = ['driver']


@admin.register(Driver)
class DriverAdmin(BaseAdmin):
    list_display = ['id32', 'name', 'device_gps']
    search_fields = ['name']
    fields = ['name', 'phone_number', 'device_gps', 'owned_by']



class DropInline(admin.StackedInline):
    model = Drop
    extra = 1  # Specifies the number of empty forms the formset should display.
    fields = ['location_name', 'address', 'location', 'order', 'travel_document', 'signature', 'visit_evidence', 'item_delivery_evidence', 'sales_visit']
    raw_id_fields = ['sales_visit']


@admin.register(Job)
class JobAdmin(BaseAdmin):
    list_display = ['id32', 'vehicle', 'trip', 'assigned_driver','status']
    list_filter = ['vehicle', 'assigned_driver', 'status']
    search_fields = ['vehicle__name', 'trip__id32']
    fields = ['vehicle', 'trip', 'assigned_driver', 'date', 'start_time', 'end_time', 'status']
    raw_id_fields = ['vehicle', 'assigned_driver', 'trip']
    inlines = [DropInline]  # Add the inline to your admin


