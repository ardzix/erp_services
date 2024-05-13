from rest_framework.routers import DefaultRouter
from .views.customer import CustomerViewSet, StoreTypeViewSet
from .views.sales import SalesOrderViewSet, SalesPaymentViewSet, RecordingSalesViewSet
from .views.trip import (
    TripTemplateViewSet,
    TripViewSet,
    CustomerVisitStatusUpdateViewSet,
)

router = DefaultRouter()
router.register('customer_visit',
                CustomerVisitStatusUpdateViewSet, basename='customer_visit')
router.register('trip_template',
                TripTemplateViewSet, basename='trip_template')
router.register('trip', TripViewSet,
                basename='trip')
router.register('store_type', StoreTypeViewSet, basename='store_type')
router.register('customer', CustomerViewSet, basename='customer')
router.register('sales_order', SalesOrderViewSet, basename='sales_order')
router.register('sales_payment', SalesPaymentViewSet, basename='sales_payment')
router.register('recording_sales', RecordingSalesViewSet,
                basename='recording_sales')
