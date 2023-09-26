from rest_framework.routers import DefaultRouter
from .views.customer import CustomerViewSet
from .views.sales import SalesOrderViewSet
from .views.canvasing import (
    TripTemplateViewSet,
    TripViewSet,
    CustomerVisitStatusUpdateViewSet
)

router = DefaultRouter()
router.register('customer_visit',
                CustomerVisitStatusUpdateViewSet, basename='customer_visit')
router.register('trip_template',
                TripTemplateViewSet, basename='trip_template')
router.register('trip', TripViewSet,
                basename='trip')
router.register('customer', CustomerViewSet, basename='customer')
router.register('sales_order', SalesOrderViewSet, basename='sales_order')
