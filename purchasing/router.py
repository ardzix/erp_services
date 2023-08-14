from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierProductViewSet, PurchaseOrderViewSet

router = DefaultRouter()
router.register('purchase_order', PurchaseOrderViewSet, basename='purchase_order')
router.register('supplier', SupplierViewSet, basename='supplier')
router.register('supplier_product', SupplierProductViewSet, basename='supplier_product')