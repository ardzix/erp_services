from rest_framework.routers import DefaultRouter
from .views.customer import CustomerViewSet
from .views.sales import SalesOrderViewSet
from .views.canvasing import (
    TripTemplateViewSet,
    TripViewSet,
    CustomerVisitStatusUpdateViewSet
)

router = DefaultRouter()
router.register('canvassing_customer_visit',
                CustomerVisitStatusUpdateViewSet, basename='canvassing_customer_visit')
router.register('canvassing_trip_template',
                TripTemplateViewSet, basename='canvassing_trip_template')
router.register('canvassing_trip', TripViewSet,
                basename='canvassing_trip')
router.register('customer', CustomerViewSet, basename='customer')
router.register('sales_order', SalesOrderViewSet, basename='sales_order')
