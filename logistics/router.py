from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, VehicleViewSet, JobViewSet, DropViewSet

router = DefaultRouter()
router.register('driver', DriverViewSet, basename='driver')
router.register('vehicle', VehicleViewSet, basename='vehicle')
router.register('job', JobViewSet, basename='job')
router.register('drop', DropViewSet, basename='drop')
