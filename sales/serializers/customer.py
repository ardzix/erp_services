from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from common.models import File
from ..models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()
    id_card_id32 = serializers.CharField(write_only=True)
    store_front_id32 = serializers.CharField(write_only=True)
    store_street_id32 = serializers.CharField(write_only=True)
    signature_id32 = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = [
            'id32',
            'name',
            'contact_number',
            'address',
            'location',
            'location_coordinate',

            'company_profile',
            'administrative_lv1',
            'administrative_lv2',
            'administrative_lv3',
            'administrative_lv4',
            'rt',
            'rw',
            'store_name',
            'payment_type',
            'store_type',

            'id_card_id32',
            'store_front_id32',
            'store_street_id32',
            'signature_id32',
            'id_card',
            'store_front',
            'store_street',
            'signature'
        ]
        read_only_fields = ['id32', 'id_card',
                            'store_front', 'store_street', 'signature']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Handle Administrative Levels
        administrative_levels = [
            'administrative_lv1', 'administrative_lv2', 'administrative_lv3', 'administrative_lv4']
        for level in administrative_levels:
            attr_instance = getattr(instance, level)
            if attr_instance:
                representation[level] = {
                    'id': attr_instance.pk,
                    'name': attr_instance.name
                }

        # Handle Files
        file_fields = ['id_card', 'store_front', 'store_street', 'signature']
        for field in file_fields:
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'id32': attr_instance.id32,
                    'url': attr_instance.file.url
                }

        # Handle Choice Fields
        choices_dicts = {
            'payment_type': dict(Customer.PAYMENT_TYPE_CHOICES),
            'store_type': dict(Customer.STORE_TYPE_CHOICES)
        }
        for field, choice_dict in choices_dicts.items():
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'key': attr_instance,
                    'value': choice_dict.get(attr_instance, ""),
                }

        return representation

    def get_location_coordinate(self, obj):
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    def validate_file_by_id32(self, value, error_message):
        """
        Helper method to validate file existence by its id32.
        """
        if not value:
            return value

        try:
            file = File.objects.get(id32=value)
            return file
        except File.DoesNotExist:
            raise serializers.ValidationError(
                error_message.format(value=value))

    def validate_id_card_id32(self, value):
        return self.validate_file_by_id32(value, "A file with id32 {value} does not exist for the ID card.")

    def validate_store_front_id32(self, value):
        return self.validate_file_by_id32(value, "A file with id32 {value} does not exist for the store front.")

    def validate_store_street_id32(self, value):
        return self.validate_file_by_id32(value, "A file with id32 {value} does not exist for the store street.")

    def validate_signature_id32(self, value):
        return self.validate_file_by_id32(value, "A file with id32 {value} does not exist for the signature.")

    def handle_location(self, validated_data):
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            longitude, latitude = location_data.split(',')
            validated_data['location'] = Point(
                float(longitude), float(latitude))
        return validated_data

    def handle_file_fields(self, validated_data, fields):
        for field_name, model_name in fields.items():
            if field_name in validated_data:
                file_object = validated_data.pop(field_name)
                validated_data[model_name] = file_object
        return validated_data

    def create(self, validated_data):
        validated_data = self.handle_location(validated_data)
        file_fields = {
            'id_card_id32': 'id_card',
            'store_front_id32': 'store_front',
            'store_street_id32': 'store_street',
            'signature_id32': 'signature'
        }
        validated_data = self.handle_file_fields(validated_data, file_fields)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.handle_location(validated_data)
        file_fields = {
            'id_card_id32': 'id_card',
            'store_front_id32': 'store_front',
            'store_street_id32': 'store_street',
            'signature_id32': 'signature'
        }
        validated_data = self.handle_file_fields(validated_data, file_fields)
        return super().update(instance, validated_data)


class CustomerListSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'store_name', 'contact_number', 'address']


class CustomerLiteSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'store_name',
                  'contact_number', 'address', 'location_coordinate']

# e920477217b35578fa1e71f7aa5b280771987b13
