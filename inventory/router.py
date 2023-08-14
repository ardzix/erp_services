from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, StockMovementViewSet

router = DefaultRouter()
router.register('product', ProductViewSet, basename='product')
router.register('stock_movement', StockMovementViewSet, basename='stock_movement')