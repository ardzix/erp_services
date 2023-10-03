from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, VehicleViewSet

router = DefaultRouter()
router.register('driver', DriverViewSet, basename='driver')
router.register('vehicle', VehicleViewSet, basename='vehicle')
