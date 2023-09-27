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
        fields = ('customer_id32', 'customer_name', 'order')
        read_only_fields = ('id32',)


class TripTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripTemplate
        fields = ['id32', 'name']
        read_only_fields = ['id32']


class TripTemplateDetailSerializer(serializers.ModelSerializer):
    trip_customers = TripCustomerSerializer(
        many=True, source='tripcustomer_set')

    class Meta:
        model = TripTemplate
        fields = ['id32', 'name', 'trip_customers']
        read_only_fields = ['id32']

    def create(self, validated_data):
        trip_customers_data = validated_data.pop('tripcustomer_set', [])
        trip_template = TripTemplate.objects.create(**validated_data)

        # For each trip customer data, create a TripCustomer instance linked to the TripTemplate
        for trip_customer_data in trip_customers_data:
            TripCustomer.objects.create(
                template=trip_template, created_by=trip_template.created_by, **trip_customer_data)

        return trip_template

    def update(self, instance, validated_data):
        trip_customers_data = validated_data.pop('tripcustomer_set', [])

        # Update the TripTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle the nested TripCustomers
        existing_trip_customers = TripCustomer.objects.filter(
            template=instance)

        # Remove TripCustomers not present in the provided data
        existing_ids = set(
            existing_trip_customers.values_list('id', flat=True))
        provided_ids = {item.get('id')
                        for item in trip_customers_data if 'id' in item}
        to_delete_ids = existing_ids - provided_ids
        TripCustomer.objects.filter(id__in=to_delete_ids).delete()

        # Create new or update existing TripCustomers
        for trip_customer_data in trip_customers_data:
            if 'id' in trip_customer_data:
                trip_customer_id = trip_customer_data.pop('id')
                TripCustomer.objects.filter(id=trip_customer_id).update(
                    updated_by=instance.updated_by, **trip_customer_data)
            else:
                TripCustomer.objects.create(
                    template=instance, created_by=instance.updated_by, **trip_customer_data)

        return instance


class TripRepresentationMixin():
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        status_dict = dict(Trip.STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_dict.get(instance.status, ""),
        }
        representation['driver'] = {
            'id': instance.driver.pk,
            'username': instance.driver.username,
            'full_name': f'{instance.driver.first_name} {instance.driver.last_name}',
        }

        return representation


class CustomerVisitSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = CustomerVisit
        fields = ['id32', 'customer', 'sales_order', 'status', 'order']
        read_only_fields = ['id32']


class TripListSerializer(TripRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'driver', 'status']
        read_only_fields = ['id32']


class TripDetailSerializer(TripRepresentationMixin, serializers.ModelSerializer):
    template = TripTemplateListSerializer()
    customer_visits = CustomerVisitSerializer(
        many=True, source='customervisit_set')

    class Meta:
        model = Trip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'driver', 'status', 'customer_visits']
        read_only_fields = ['id32']


class CustomerVisitReportSerializer(serializers.ModelSerializer):
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
            raise serializers.ValidationError(
                _("End date must be after start date."))
        return data

    def validate_salesperson_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("Salesperson with this username does not exist."))
        return user

    def validate_driver_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("Driver with this username does not exist."))
        return user


class CustomerVisitStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerVisit
        fields = ['status']
