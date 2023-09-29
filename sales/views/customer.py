from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers.customer import CustomerSerializer, CustomerListSerializer
from ..models import Customer


def get_customer_create_chema():
    return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Enter the customer's name",
                    maxLength=100,
                    minLength=1,
                    example="John Doe"
                ),
                'contact_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Enter the contact number",
                    maxLength=15,
                    minLength=1,
                    example="1234567890"
                ),
                'address': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Enter the address",
                    minLength=1,
                    example="123 Main St"
                ),
                'location': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Enter the location coordinates as longitude and latitude (e.g., 107,-7)",
                    example="107,-7"
                ),
                'company_profile': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Select the company profile associated with the customer",
                    example=1
                )
            },
            required=['name', 'contact_number', 'address', 'company_profile']
        )


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
    pagination_class = CustomPagination  # Add your custom pagination class if needed

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    @swagger_auto_schema(
        request_body=get_customer_create_chema()
    )
    def create(self, requests, *args, **kwargs):
        return super().create(requests, *args, **kwargs)
    
    @swagger_auto_schema(
        request_body=get_customer_create_chema()
    )
    def update(self, requests, *args, **kwargs):
        return super().update(requests, *args, **kwargs)


    
