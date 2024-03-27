from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
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
    


class ProductionTrackingFilter(django_filters.FilterSet):
    start_time_range = django_filters.CharFilter(method='filter_start_time_range', help_text=_('Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))
    end_time_range = django_filters.CharFilter(method='filter_end_time_range', help_text=_('Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))
    work_center_warehouse_id32 = django_filters.CharFilter(field_name='work_center_warehouse__id32', lookup_expr='exact')

    def filter_start_time_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(start_time__gte=start_date, start_time__lte=end_date)
        return queryset

    def filter_end_time_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(end_time__gte=start_date, end_time__lte=end_date)
        return queryset
    class Meta:
        model = ProductionTracking
        fields = ['start_time_range', 'end_time_range', 'work_center_warehouse_id32']


class ProductionTrackingViewSet(viewsets.ModelViewSet):
    queryset = ProductionTracking.objects.all()
    serializer_class = ProductionTrackingSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filterset_class = ProductionTrackingFilter
    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['work_center_warehouse__name']
    lookup_field = 'id32'
