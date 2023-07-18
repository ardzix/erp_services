from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesOrderViewSet, CustomerViewSet

router = DefaultRouter()
router.register('customer', CustomerViewSet, basename='customer')
router.register('sales_order', SalesOrderViewSet, basename='sales_order')