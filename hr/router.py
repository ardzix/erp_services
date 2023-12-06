from rest_framework.routers import DefaultRouter
from .views.attendance import AttendanceViewSet
from .views.employee import DepartmentViewSet, EmployeeViewSet, LocationTrackerViewSet

router = DefaultRouter()
router.register('attendance', AttendanceViewSet, basename='attendance')
router.register('department', DepartmentViewSet, basename='department')
router.register('employee', EmployeeViewSet, basename='employee')
router.register('location_tracker', LocationTrackerViewSet, basename='location_tracker')
