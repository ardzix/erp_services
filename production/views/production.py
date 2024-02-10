from rest_framework import viewsets
from ..models import ProductionOrder, WorkOrder, ProductionTracking
from ..serializers.production import ProductionOrderSerializer, WorkOrderSerializer, ProductionTrackingSerializer

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

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
