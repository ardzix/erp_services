from rest_framework.routers import DefaultRouter
from .views.customer import CustomerViewSet
from .views.sales import SalesOrderViewSet
from .views.canvasing import (
    CanvassingTripTemplateViewSet,
    CanvassingTripViewSet,
    CanvassingCustomerVisitStatusUpdateViewSet
)

router = DefaultRouter()
router.register('canvassing_customer_visit',
                CanvassingCustomerVisitStatusUpdateViewSet, basename='canvassing_customer_visit')
router.register('canvassing_trip_template',
                CanvassingTripTemplateViewSet, basename='canvassing_trip_template')
router.register('canvassing_trip', CanvassingTripViewSet,
                basename='canvassing_trip')
router.register('customer', CustomerViewSet, basename='customer')
router.register('sales_order', SalesOrderViewSet, basename='sales_order')
