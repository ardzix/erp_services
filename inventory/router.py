from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, StockMovementViewSet, UnitViewSet

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('product', ProductViewSet, basename='product')
router.register('stock_movement', StockMovementViewSet, basename='stock_movement')
router.register('unit', UnitViewSet, basename='unit')