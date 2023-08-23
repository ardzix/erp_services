from rest_framework.routers import DefaultRouter
from .views import SalesOrderViewSet, CustomerViewSet
from .views.canvasing import (
    CanvasingTripTemplateViewSet,
    CanvasingTripViewSet,
    CanvasingCustomerVisitStatusUpdateViewSet
)

router = DefaultRouter()
router.register('canvasing_customer_visit',
                CanvasingCustomerVisitStatusUpdateViewSet, basename='canvasing_customer_visit')
router.register('canvasing_trip_template',
                CanvasingTripTemplateViewSet, basename='canvasing_trip_template')
router.register('canvasing_trip', CanvasingTripViewSet,
                basename='canvasing_trip')
router.register('customer', CustomerViewSet, basename='customer')
router.register('sales_order', SalesOrderViewSet, basename='sales_order')
