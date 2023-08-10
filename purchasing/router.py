from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet

router = DefaultRouter()
router.register('supplier', SupplierViewSet, basename='supplier')