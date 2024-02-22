from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from libs.pagination import CustomPagination
from libs.filter import CreatedAtFilterMixin
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from ..models import ProductionOrder, WorkOrder, ProductionTracking
from ..serializers.production import ProductionOrderSerializer, WorkOrderSerializer, ProductionTrackingSerializer

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filterset_class = CreatedAtFilterMixin
    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['product__name']
    lookup_field = 'id32'

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filterset_class = CreatedAtFilterMixin
    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['production_order__product__name']
    lookup_field = 'id32'


    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('work_order_status_filter', None)
        if status_filter == 'ordered':
            queryset = queryset.filter(start_time__isnull=True)
        elif status_filter == 'started':
            queryset = queryset.filter(start_time__isnull=False, end_time__isnull=True)
        elif status_filter == 'finished':
            queryset = queryset.filter(end_time__isnull=False)
        return queryset

class ProductionTrackingViewSet(viewsets.ModelViewSet):
    queryset = ProductionTracking.objects.all()
    serializer_class = ProductionTrackingSerializer
