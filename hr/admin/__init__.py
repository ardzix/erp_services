from django.contrib import admin
from hr.models import Department, Employee, Leave, Attendance, Performance
from libs.admin import BaseAdmin

@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ['id32', 'name']
    search_fields = ['id32', 'name']

@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ['id32', 'user', 'department']
    list_filter = ['department']
    search_fields = ['id32', 'user__username', 'user__first_name', 'user__last_name']
    fields = ['user', 'department']

@admin.register(Leave)
class LeaveAdmin(BaseAdmin):
    list_display = ['id32', 'employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['employee', 'status']
    search_fields = ['id32', 'employee__user__username', 'employee__user__first_name', 'employee__user__last_name', 'leave_type']
    fields = ['employee', 'leave_type', 'start_date', 'end_date', 'status']

@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ['id32', 'employee', 'clock_in', 'clock_out']
    list_filter = ['employee']
    search_fields = ['id32', 'employee__user__username', 'employee__user__first_name', 'employee__user__last_name']
    fields = ['employee', 'clock_in', 'clock_out', 'clock_in_location', 'clock_out_location', 'able_checkout']

@admin.register(Performance)
class PerformanceAdmin(BaseAdmin):
    list_display = ['id32', 'employee', 'rating', 'review']
    list_filter = ['employee']
    search_fields = ['id32', 'employee__user__username', 'employee__user__first_name', 'employee__user__last_name']
    fields = ['employee', 'rating', 'review']
