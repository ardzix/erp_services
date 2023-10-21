from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, 
    ProductViewSet, 
    UnitViewSet,
    WarehouseViewSet
)
from .views.stock_movement import StockMovementViewSet, StockMovementItemStatusUpdateViewSet
from .views.warehouse_stock import WarehouseStockViewSet

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('product', ProductViewSet, basename='product')
router.register('stock_movement', StockMovementViewSet, basename='stock_movement')
router.register('stock_movement_item', StockMovementItemStatusUpdateViewSet, basename='stock_movement_item')
router.register('unit', UnitViewSet, basename='unit')
router.register('warehouse', WarehouseViewSet, basename='warehouse')
router.register('warehouse_stock', WarehouseStockViewSet, basename='warehouse_stock')