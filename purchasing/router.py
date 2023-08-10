from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierProductViewSet

router = DefaultRouter()
router.register('supplier', SupplierViewSet, basename='supplier')
router.register('supplier_product', SupplierProductViewSet, basename='supplier_product')