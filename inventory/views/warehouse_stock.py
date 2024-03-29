from rest_framework import viewsets, permissions, filters
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from django.db.models import Sum
from ..models import WarehouseStock
from ..serializers.stock import WarehouseStockSerializer, DistinctWarehouseStockSerializer


class WarehouseStockFilter(django_filters.FilterSet):
    warehouse_id32 = django_filters.CharFilter(
        field_name='warehouse__id32', lookup_expr='exact')
    product_id32 = django_filters.CharFilter(
        field_name='product__id32', lookup_expr='exact')
    unit_id32 = django_filters.CharFilter(
        field_name='unit__id32', lookup_expr='exact')
    expires_before_or_on = django_filters.DateFilter(
        field_name="expire_date", lookup_expr='lte')
    expires_after = django_filters.DateFilter(
        field_name="expire_date", lookup_expr='gt')

    class Meta:
        model = WarehouseStock
        fields = ['warehouse_id32', 'product_id32', 'unit_id32',
                  'expires_before_or_on', 'expires_after']


class WarehouseStockViewSet(viewsets.ModelViewSet):
    queryset = WarehouseStock.objects.filter(quantity__gt=0)
    serializer_class = WarehouseStockSerializer
    filter_backends = (filters.OrderingFilter,
                       django_filters.DjangoFilterBackend,
                       filters.SearchFilter)
    filterset_class = WarehouseStockFilter
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    lookup_field = 'id32'
    search_fields = ['warehouse__name', 'product__name']

    def get_serializer_class(self):
        if self.action == 'distinct':
            return DistinctWarehouseStockSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'], name='Distinct Warehouse Stock')
    def distinct(self, request, *args, **kwargs):
        # Start with the default queryset
        queryset = self.queryset

        # Apply filters
        filter_class = self.filterset_class
        if filter_class:
            queryset = filter_class(self.request.GET, queryset=queryset).qs

        queryset = queryset.values(
            'warehouse__id32', 'warehouse__name', 'product__id32', 'product__name',
            'unit__id32', 'unit__name', 'unit__symbol'
        ).annotate(total_quantity=Sum('quantity'))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
