from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjangoCoreValidationError
from django.contrib.auth.models import User
from rest_framework import serializers
from logistics.models import Vehicle
from libs.utils import validate_file_by_id32, handle_file_fields
from libs.constants import SKIPPED, COMPLETED
from libs.serializers import UsernamesField
from ..models import (
    TripTemplate,
    TripCustomer,
    Trip,
    CustomerVisit,
    Customer,
    CustomerVisitReport,
    SalesOrder
)
from .customer import CustomerLiteSerializer


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



class VehiclesField(serializers.RelatedField):
    def to_representation(self, value):
        return value.id32

    def to_internal_value(self, data):
        try:
            return Vehicle.objects.get(id32=data)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(
                f"Vehicle with id32 {data} does not exist.")


class TripTemplateDetailSerializer(serializers.ModelSerializer):
    trip_customers = TripCustomerSerializer(
        many=True, source='tripcustomer_set')
    pic_usernames = UsernamesField(
        source='pic', many=True,  required=False, queryset=User.objects.all())
    collector_pic_usernames = UsernamesField(
        source='collector_pic', many=True,  required=False, queryset=User.objects.all())
    vehicle_id32s = VehiclesField(
        source='vehicles', many=True, write_only=True, required=False, queryset=Vehicle.objects.all())

    class Meta:
        model = TripTemplate
        fields = ['id32', 'name', 'trip_customers',
                  'pic_usernames', 'collector_pic_usernames', 
                  'vehicle_id32s', 'vehicles']
        read_only_fields = ['id32', 'vehicles']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['vehicles'] = [
            {'id32': vehicle.id32, 'name': f'{vehicle.name} ({vehicle.license_plate})'} for vehicle in instance.vehicles.all()]
        return representation

    def create(self, validated_data):
        trip_customers_data = validated_data.pop('tripcustomer_set', [])
        pic = validated_data.pop('pic', [])
        collector_pic = validated_data.pop('collector_pic', [])
        vehicles = validated_data.pop('vehicles', [])

        trip_template = TripTemplate.objects.create(**validated_data)

        # Assign the provided users to pic
        trip_template.pic.set(pic)
        trip_template.collector_pic.set(collector_pic)
        # Assign the provided vehicles
        trip_template.vehicles.set(vehicles)

        # For each trip customer data, create a TripCustomer instance linked to the TripTemplate
        for trip_customer_data in trip_customers_data:
            TripCustomer.objects.create(
                template=trip_template, **trip_customer_data)

        return trip_template

    def update(self, instance, validated_data):
        trip_customers_data = validated_data.pop('tripcustomer_set', [])
        pic = validated_data.pop('pic', [])
        collector_pic = validated_data.pop('collector_pic', [])
        vehicles = validated_data.pop('vehicles', [])

        # Update the TripTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Assign the provided users to pic
        instance.pic.set(pic)
        instance.collector_pic.set(collector_pic)
        # Assign the provided vehicles
        instance.vehicles.set(vehicles)

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
        type_dict = dict(Trip.TYPE_CHOICES)
        representation['type'] = {
            'key': instance.type,
            'value': type_dict.get(instance.type, ""),
        }
        if instance.vehicle:
            representation['vehicle'] = {
                'id32': instance.vehicle.id32,
                'name': instance.vehicle.name,
                'license_plate': instance.vehicle.license_plate,
                'driver': instance.vehicle.driver.name if instance.vehicle.driver else None,
                'warehouse_id32': instance.vehicle.warehouse.id32 if instance.vehicle.warehouse else None
            }
        if instance.salesperson:
            representation['salesperson'] = {
                'username': instance.salesperson.username,
                'full_name': f'{instance.salesperson.first_name} {instance.salesperson.last_name}'
            }
        if instance.collector:
            representation['collector'] = {
                'username': instance.collector.username,
                'full_name': f'{instance.collector.first_name} {instance.collector.last_name}'
            }

        return representation


class CustomerVisitSerializer(serializers.ModelSerializer):
    customer = CustomerLiteSerializer()

    class Meta:
        model = CustomerVisit
        fields = ['id32', 'customer', 'sales_order', 'status', 'order']
        read_only_fields = ['id32']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        status_dict = dict(Trip.STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_dict.get(instance.status, ""),
        }
        if instance.sales_order:
            representation['sales_order'] = {
                'id32': instance.sales_order.id32,
                'str': instance.sales_order.__str__()
            }

        return representation


class TripListSerializer(TripRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'collector', 'vehicle', 'status']
        read_only_fields = ['id32']


class TripDetailSerializer(TripRepresentationMixin, serializers.ModelSerializer):
    template = TripTemplateListSerializer(read_only=True)
    customer_visits = CustomerVisitSerializer(
        many=True, source='customervisit_set', read_only=True)
    last_position = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id32', 'template', 'date', 'type', 'salesperson', 'collector',
                  'vehicle', 'status', 'customer_visits', 'stock_movement_id32s',
                  'last_position']
        read_only_fields = ['id32', 'vehicle',
                            'salesperson', 'customer_visits', 'template']

    def get_last_position(self, obj):
        last_visit = obj.customervisit_set.filter(status__in=[COMPLETED, SKIPPED]).order_by('order').last()
        return last_visit.customer.location_coordinate if last_visit and last_visit.customer else None

class TripUpdateSerializer(TripRepresentationMixin, serializers.ModelSerializer):
    salesperson_username = serializers.CharField(write_only=True)
    collector_username = serializers.CharField(write_only=True)
    vehicle_id32 = serializers.CharField(write_only=True)

    class Meta:
        model = Trip
        fields = ['date', 'type', 'salesperson_username', 'collector_username',
                  'vehicle_id32', 'status']

    def update(self, instance, validated_data):
        if 'vehicle_id32' in validated_data:
            validated_data['vehicle'] = validated_data.pop('vehicle_id32')

        if 'salesperson_username' in validated_data:
            validated_data['salesperson'] = validated_data.pop(
                'salesperson_username')

        if 'collector_username' in validated_data:
            validated_data['collector'] = validated_data.pop(
                'collector_username')

        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(list(e))

    def validate_salesperson_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("Salesperson with this username does not exist."))
        return user

    def validate_collector_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("Collector with this username does not exist."))
        return user

    def validate_vehicle_id32(self, value):
        try:
            vehicle = Vehicle.objects.get(id32=value)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(
                _("Vehicle with this id32 does not exist."))
        return vehicle


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
    vehicle_id32 = serializers.CharField(write_only=True, required=False)
    type = serializers.ChoiceField(choices=Trip.TYPE_CHOICES)

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

    def validate_vehicle_id32(self, value):
        try:
            vehicle = Vehicle.objects.get(id32=value)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(
                _("Vehicle with this id32 does not exist."))
        return vehicle


class CustomerVisitStatusSerializer(serializers.ModelSerializer):
    sales_order_id32 = serializers.CharField(write_only=True, required=False)
    visit_evidence_id32 = serializers.CharField(
        write_only=True, required=False)
    item_delivery_evidence_id32 = serializers.CharField(
        write_only=True, required=False)
    signature_id32 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomerVisit
        fields = ['id32', 'status', 'sales_order_id32', 'sales_order', 'notes',
                  'item_delivery_evidence_id32', 'item_delivery_evidence',
                  'visit_evidence_id32', 'visit_evidence',
                  'signature_id32', 'signature']
        read_only_fields = ['id32', 'sales_order',
                            'visit_evidence', 'item_delivery_evidence', 'signature']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.sales_order:
            representation['sales_order'] = {
                'id32': instance.sales_order.id32,
                'str': instance.sales_order.__str__()
            }

        status_dict = dict(Trip.STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_dict.get(instance.status, ""),
        }

        # Handle Files
        # For each file field, if the attribute exists on the instance,
        # add its 'id32' and 'url' to the representation dictionary.
        file_fields = ['visit_evidence', 'signature', 'item_delivery_evidence']
        for field in file_fields:
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'id32': attr_instance.id32,
                    'url': attr_instance.file.url
                }

        return representation

    def validate_sales_order_id32(self, value):
        try:
            SalesOrder.objects.get(id32=value)
        except SalesOrder.DoesNotExist:
            raise serializers.ValidationError(
                _("SalesOrder with this id32 does not exist."))
        return value

    def validate_visit_evidence_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the visit evidence.")

    def validate_item_delivery_evidence_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the visit evidence.")

    def validate_signature_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the signature.")

    def update(self, instance, validated_data):
        if 'sales_order_id32' in validated_data:
            sales_order_id32 = validated_data.pop('sales_order_id32')
            sales_order = SalesOrder.objects.get(id32=sales_order_id32)
            validated_data['sales_order'] = sales_order

        file_fields = {
            'item_delivery_evidence_id32': 'item_delivery_evidence',
            'visit_evidence_id32': 'visit_evidence',
            'signature_id32': 'signature'
        }
        validated_data = handle_file_fields(validated_data, file_fields)
        try:
            return super().update(instance, validated_data)
        except DjangoCoreValidationError as e:
            raise serializers.ValidationError(e.messages)
