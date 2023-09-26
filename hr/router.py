from rest_framework.routers import DefaultRouter
from .views.attendance import AttendanceViewSet

router = DefaultRouter()
router.register('attendance', AttendanceViewSet, basename='attendance')
