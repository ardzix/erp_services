from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoCoreValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from libs.utils import validate_file_by_id32, handle_file_fields
from sales.serializers.sales import OrderItemSerializer
from sales.models import Trip
from ..models import Drop, Job, Vehicle, Driver, STATUS_CHOICES


class LocationMixin:
    def get_location(self, obj):
        """
        Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute.
        """
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        status_dict = dict(STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_dict.get(instance.status, ""),
        }
        return representation


class FileMixin:

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        file_fields = ['travel_document', 'visit_evidence',
                       'signature', 'item_delivery_evidence']
        for field in file_fields:
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'id32': attr_instance.id32,
                    'url': attr_instance.file.url
                }

        return representation


class DropListSerializer(LocationMixin, serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Drop
        fields = ['id32', 'location_name', 'location',
                  'address', 'order', 'status', 'retrieve_payment']
        read_only_fields = ['id32']


class DropDetailSerializer(LocationMixin, FileMixin, serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Drop
        fields = [
            'id32', 'job', 'location_name', 'address', 'location', 'order',
            'retrieve_payment', 'travel_document', 'signature', 'visit_evidence',
            'item_delivery_evidence', 'status', 'sales_visit', 'sales_order', 'items', 'notes'
        ]
        read_only_fields = ['id32', 'job']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['job'] = {
            'id32': instance.job.id32,
            'str': instance.job.__str__()
        }
        if instance.sales_visit:
            representation['sales_visit'] = {
                'id32': instance.sales_visit.id32,
                'str': instance.sales_visit.__str__()
            }
        if instance.sales_order:
            representation['sales_order'] = {
                'id32': instance.sales_order.id32,
                'str': instance.sales_order.__str__()
            }
        return representation


class DropUpdateSerializer(FileMixin, serializers.ModelSerializer):
    travel_document_id32 = serializers.CharField(
        write_only=True, required=False)
    signature_id32 = serializers.CharField(write_only=True, required=False)
    visit_evidence_id32 = serializers.CharField(
        write_only=True, required=False)
    item_delivery_evidence_id32 = serializers.CharField(
        write_only=True, required=False)

    class Meta:
        model = Drop
        fields = ['travel_document', 'signature', 'visit_evidence', 'item_delivery_evidence',
                  'travel_document_id32', 'signature_id32', 'visit_evidence_id32', 'item_delivery_evidence_id32', 'status', 'notes']
        read_only_fields = ['travel_document', 'signature',
                            'visit_evidence', 'item_delivery_evidence']

    def validate_travel_document_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the travel document.")

    def validate_signature_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the signature.")

    def validate_visit_evidence_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the visit evidence.")

    def validate_item_delivery_evidence_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the item delivery evidence.")

    def update(self, instance, validated_data):

        file_fields = {
            'travel_document_id32': 'travel_document',
            'signature_id32': 'signature',
            'visit_evidence_id32': 'visit_evidence',
            'item_delivery_evidence_id32': 'item_delivery_evidence'
        }
        validated_data = handle_file_fields(validated_data, file_fields)
        try:
            return super().update(instance, validated_data)
        except DjangoCoreValidationError as e:
            raise serializers.ValidationError(e.messages)


class JobRepresentationMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['vehicle'] = {
            'id32': instance.vehicle.id32,
            'str': instance.vehicle.__str__()
        }
        representation['trip'] = {
            'id32': instance.trip.id32,
            'str': instance.trip.__str__()
        }
        if instance.assigned_driver:
            representation['assigned_driver'] = {
                'id32': instance.assigned_driver.id32,
                'str': instance.assigned_driver.__str__()
            }
        status_dict = dict(STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_dict.get(instance.status, ""),
        }
        return representation


class JobListSerializer(JobRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id32', 'vehicle', 'trip',
                  'assigned_driver', 'date', 'status']


class JobDetailSerializer(JobRepresentationMixin, serializers.ModelSerializer):
    drops = DropListSerializer(many=True, read_only=True)
    vehicle_id32 = serializers.CharField(write_only=True)
    trip_id32 = serializers.CharField(write_only=True)
    assigned_driver_id32 = serializers.CharField(write_only=True)

    class Meta:
        model = Job
        fields = [
            'id32', 'vehicle', 'vehicle_id32', 'trip', 'trip_id32', 'assigned_driver', 'assigned_driver_id32', 'date', 'start_time', 'end_time', 'status', 'drops'
        ]
        read_only_fields = ['id32', 'vehicle', 'trip', 'assigned_driver']

    def validate_id32(self, id32, model, error_msg):
        try:
            return model.objects.get(id32=id32)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(error_msg)

    def validate_vehicle_id32(self, value):
        return self.validate_id32(value, Vehicle, _("Provided vehicle_id32 does not match any Vehicle records."))

    def validate_trip_id32(self, value):
        return self.validate_id32(value, Trip, _("Provided trip_id32 does not match any Trip records."))
    
    def validate_assigned_driver_id32(self, value):
        return self.validate_id32(value, Driver, _("Provided assigned_driver_id32 does not match any Driver records."))

    def handle_related_object(self, validated_data, field_name, obj):
        if obj:
            validated_data[field_name] = obj

    def handle_related_objects(self, validated_data):
        # A list of tuples with (field_name, field_id32_key)
        related_objects = [
            ('vehicle', 'vehicle_id32'),
            ('trip', 'trip_id32'),
            ('assigned_driver', 'assigned_driver_id32'),
        ]
        
        for field_name, field_id32_key in related_objects:
            if field_id32_key in validated_data:
                self.handle_related_object(validated_data, field_name, validated_data.pop(field_id32_key))

    def create(self, validated_data):
        self.handle_related_objects(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.handle_related_objects(validated_data)
        return super().update(instance, validated_data)

