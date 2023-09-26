from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from inventory.models import Product
from ..models import (
    TripTemplate,
    TripCustomer,
    Trip,
    CustomerVisit,
    Customer,
    CustomerVisitReport
)
from .customer import CustomerSerializer


class TripCustomerSerializer(serializers.ModelSerializer):
    customer_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=Customer.objects.all(),
        help_text=_("Select customer intended for this canvasing"),
        source='customer'
    )
    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True,
        help_text=_("Name of the customer")
    )
    class Meta:
        model = TripCustomer
        fields = ('customer_id32', 'customer_name', 'order', 'products')
        read_only_fields = ('id32',)


class TripTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripTemplate
        fields = ['id32', 'name']
        read_only_fields = ['id32']


class TripTemplateDetailSerializer(serializers.ModelSerializer):
    customers = CustomerSerializer(
        many=True, source='canvasingcustomer_set')

    class Meta:
        model = TripTemplate
        fields = ['id32', 'name', 'customers']
        read_only_fields = ['id32']

class TripListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'driver', 'status']
        read_only_fields = ['id32']


class CustomerVisitSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    class Meta:
        model = CustomerVisit
        fields = ['id32', 'customer', 'sales_order', 'status', 'order']
        read_only_fields = ['id32']


class TripDetailSerializer(serializers.ModelSerializer):
    template = TripTemplateListSerializer()
    customer_visits = CustomerVisitSerializer(
        many=True, source='customervisit_set')
    class Meta:
        model = Trip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'driver', 'status', 'customer_visits']
        read_only_fields = ['id32']


class CanvassingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerVisitReport
        fields = ['id32', 'trip', 'customer_visit',
                  'customer', 'status', 'sold_products']
        read_only_fields = ['id32']

class GenerateTripsSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    salesperson_username = serializers.CharField(write_only=True)
    driver_username = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(_("End date must be after start date."))
        return data

    def validate_salesperson_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Salesperson with this username does not exist."))
        return user

    def validate_driver_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Driver with this username does not exist."))
        return user


class CustomerVisitStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerVisit
        fields = ['status']
