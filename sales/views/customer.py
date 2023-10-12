from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers.customer import CustomerSerializer, CustomerListSerializer
from ..models import Customer


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
        return CustomerSerializer

    def create(self, requests, *args, **kwargs):
        return super().create(requests, *args, **kwargs)

    def update(self, requests, *args, **kwargs):
        return super().update(requests, *args, **kwargs)


    
