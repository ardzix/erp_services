from rest_framework.routers import DefaultRouter
from .views.bom import BillOfMaterialsViewSet
from .views.production import ProductionOrderViewSet, WorkOrderViewSet, ProductionTrackingViewSet

router = DefaultRouter()
router.register('bill-of-materials', BillOfMaterialsViewSet, basename='bill-of-materials')
router.register('production-order', ProductionOrderViewSet, basename='production-order')
router.register('work-order', WorkOrderViewSet, basename='work-order')
router.register('production-tracking', ProductionTrackingViewSet, basename='production-tracking')
