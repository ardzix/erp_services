from django.contrib.gis.db.models import Avg
from django.db import connection
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from libs.pagination import CustomPagination
from ..serializers.customer import CustomerSerializer, CustomerListSerializer, CustomerMapSerializer, StoreTypeSerializer
from ..models import Customer, StoreType


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

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'map':
            return CustomerMapSerializer
        return CustomerSerializer

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