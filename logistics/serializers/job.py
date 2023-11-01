from django.core.exceptions import ValidationError as DjangoCoreValidationError
from rest_framework import serializers
from libs.utils import validate_file_by_id32, handle_file_fields
from sales.serializers.sales import OrderItemSerializer
from ..models import Drop, Job, STATUS_CHOICES


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
            'id32', 'job', 'location_name', 'address', 'location', 'order', 'retrieve_payment',
            'travel_document', 'signature', 'visit_evidence', 'item_delivery_evidence', 'status', 'items'
        ]
        read_only_fields = ['id32', 'job']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['job'] = {
            'id32': instance.job.id32,
            'str': instance.job.__str__()
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
                  'travel_document_id32', 'signature_id32', 'visit_evidence_id32', 'item_delivery_evidence_id32',  'status']
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


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id32', 'vehicle', 'trip',
                  'assigned_driver', 'date', 'status']


class JobDetailSerializer(serializers.ModelSerializer):
    drops = DropListSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = [
            'id32', 'vehicle', 'trip', 'assigned_driver', 'date', 'start_time', 'end_time', 'status', 'drops'
        ]
        read_only_fields = ['id32', 'vehicle', 'trip', 'assigned_driver']

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
