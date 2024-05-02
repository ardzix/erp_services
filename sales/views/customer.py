from django.contrib.gis.db.models import Avg
from django.db import connection
from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, filters
from libs.pagination import CustomPagination
from libs.filter import CreatedAtFilterMixin
from ..serializers.customer import CustomerSerializer, CustomerListSerializer, CustomerMapSerializer, StoreTypeSerializer, CustomerCreateSerializer
from ..models import Customer, StoreType, OrderItem


class CustomerFilter(CreatedAtFilterMixin):
    id32s = django_filters.CharFilter(method='filter_by_id32s')
    order_created_at_range = django_filters.CharFilter(method='filter_order_created_at_range', help_text=_('Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))

    def filter_order_created_at_range(self, queryset, name, value):
        return queryset


class StoreTypeViewSet(viewsets.ModelViewSet):
    lookup_field = 'id32'
    queryset = StoreType.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    serializer_class = StoreTypeSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer API endpoints.

    retrieve:
    Return a customer instance based on the given id32.

    list:
    Return a list of all existing customers.

    create:
    Create a new customer instance. Ensure that all required fields are provided.

    delete:
    Remove an existing customer.

    update:
    Update fields in an existing customer. Ensure that all required fields are provided.

    partial_update:
    Update certain fields in an existing customer without affecting others.

    """
    lookup_field = 'id32'
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = CustomerFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'map':
            return CustomerMapSerializer
        elif self.action == 'create':
            return CustomerCreateSerializer
        return CustomerSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        order_created_at_range = request.query_params.get("order_created_at_range")
        order_items = OrderItem.objects.filter(order__customer__in=queryset)
        if order_created_at_range:
            order_created_at_range = order_created_at_range.split(',')
            if len(order_created_at_range) == 2:
                start_date, end_date = order_created_at_range
                order_items = order_items.filter(order__created_at__gte=start_date, order__created_at__lte=end_date)
        
        context = {"order_items": order_items}

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True, context=context)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, context=context)
            return self.get_paginated_response(serializer.data)

    def create(self, requests, *args, **kwargs):
        return super().create(requests, *args, **kwargs)

    def update(self, requests, *args, **kwargs):
        return super().update(requests, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def map(self, request):
        # Define the SQL to fetch average latitude and longitude
        raw_sql = """
        SELECT 
            AVG(ST_Y(location::geometry)) as avg_latitude, 
            AVG(ST_X(location::geometry)) as avg_longitude 
        FROM sales_customer
        """
        
        # Execute the raw SQL
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            avg_coords = cursor.fetchone()

        # Fetching serialized data
        queryset = self.get_queryset()
        serializer = CustomerMapSerializer(queryset, many=True)

        return Response({
            "center": {
                "latitude": avg_coords[0],
                "longitude": avg_coords[1]
            },
            "markers": serializer.data
        })