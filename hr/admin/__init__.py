from django.contrib import admin
from libs.admin import ApproveRejectMixin, BaseAdmin
from ..models import Department, Employee, Leave, Attendance, Performance

@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ['name']

@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ['user', 'department']
    list_filter = ['department']

@admin.register(Leave)
class LeaveAdmin(BaseAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['status']

@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    list_display = ['employee', 'date', 'clock_in_time', 'clock_out_time']

@admin.register(Performance)
class PerformanceAdmin(BaseAdmin):
    list_display = ['employee', 'rating']
