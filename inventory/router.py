from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, 
    ProductViewSet, 
    StockMovementViewSet, 
    StockMovementItemViewSet, 
    UnitViewSet,
    WarehouseViewSet
)

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('product', ProductViewSet, basename='product')
router.register('stock_movement', StockMovementViewSet, basename='stock_movement')
router.register('stock_movement_item', StockMovementItemViewSet, basename='stock_movement_item')
router.register('unit', UnitViewSet, basename='unit')
router.register('warehouse', WarehouseViewSet, basename='warehouse')