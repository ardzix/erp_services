from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from common.models import File
from libs.utils import validate_file_by_id32, handle_file_fields, handle_location
from ..models import Customer, StoreType, OrderItem


class StoreTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreType
        fields = [
            'id32',
            'name',
            'description',
        ]
        read_only_fields = ['id32']

class CustomerSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()
    id_card_id32 = serializers.CharField(write_only=True, required=False)
    store_front_id32 = serializers.CharField(write_only=True, required=False)
    store_street_id32 = serializers.CharField(write_only=True, required=False)
    signature_id32 = serializers.CharField(write_only=True, required=False)
    store_type_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=StoreType.objects.all(),
        source="store_type",
        required=False,
        write_only=True
    )

    class Meta:
        model = Customer
        fields = [
            'id32',
            'address',
            'administrative_lv1',
            'administrative_lv2',
            'administrative_lv3',
            'administrative_lv4',
            'company_profile',
            'contact_number',
            'credit_limit_amount',
            'credit_limit_qty',
            'due_date',
            'id_card',
            'id_card_id32',
            'location',
            'location_coordinate',
            'name',
            'payment_type',
            'rt',
            'rw',
            'signature',
            'signature_id32',
            'store_front',
            'store_front_id32',
            'store_name',
            'store_street',
            'store_street_id32',
            'store_type',
            'store_type_id32'
        ]

        read_only_fields = ['id32', 'id_card', 'store_type',
                            'store_front', 'store_street', 'signature']

    def to_representation(self, instance):
        """
        Convert the `instance` into its complex data representation.

        This method extends the default `to_representation` method 
        to include custom representations for administrative levels, 
        files, and choice fields of the instance.

        Parameters:
        - instance (Model instance): The model instance to be serialized.

        Returns:
        - dict: A dictionary representing the serialized data of the instance.
        """
        
        representation = super().to_representation(instance)

        # Handle Administrative Levels
        # For each administrative level, if the attribute exists on the instance,
        # add its 'id' and 'name' to the representation dictionary.
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
        # For each file field, if the attribute exists on the instance,
        # add its 'id32' and 'url' to the representation dictionary.
        file_fields = ['id_card', 'store_front', 'store_street', 'signature']
        for field in file_fields:
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'id32': attr_instance.id32,
                    'url': attr_instance.file.url
                }

        # Handle Choice Fields
        # For each choice field, if the attribute exists on the instance,
        # add its key and corresponding value to the representation dictionary.
        choices_dicts = {
            'payment_type': dict(Customer.PAYMENT_TYPE_CHOICES)
        }
        for field, choice_dict in choices_dicts.items():
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'key': attr_instance,
                    'value': choice_dict.get(attr_instance, ""),
                }

        if instance.store_type:
            representation['store_type'] = {
                'id32': instance.store_type.id32,
                'name': instance.store_type.name
            }
        return representation


    def get_location_coordinate(self, obj):
        """
        Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute.
        """
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    def validate_id_card_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the ID card.")

    def validate_store_front_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the store front.")

    def validate_store_street_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the store street.")

    def validate_signature_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the signature.")

    def create(self, validated_data):
        """
        Overrides the default create method to handle location and file fields before creating an instance.

        Parameters:
        - validated_data (dict): The data validated by the serializer.

        Returns:
        - instance: The created model instance.
        """
        validated_data = handle_location(validated_data)
        file_fields = {
            'id_card_id32': 'id_card',
            'store_front_id32': 'store_front',
            'store_street_id32': 'store_street',
            'signature_id32': 'signature'
        }
        validated_data = handle_file_fields(validated_data, file_fields)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Overrides the default update method to handle location and file fields before updating an instance.

        Parameters:
        - instance (Model instance): The model instance to be updated.
        - validated_data (dict): The data validated by the serializer.

        Returns:
        - instance: The updated model instance.
        """
        validated_data = handle_location(validated_data)
        file_fields = {
            'id_card_id32': 'id_card',
            'store_front_id32': 'store_front',
            'store_street_id32': 'store_street',
            'signature_id32': 'signature'
        }
        validated_data = handle_file_fields(validated_data, file_fields)
        return super().update(instance, validated_data)



class CustomerCreateSerializer(CustomerSerializer):
    

    class Meta:
        model = Customer
        fields = [
            'id32',
            'address',
            'contact_number',
            'name',
            'id_card_id32',
            'store_front',
            'store_front_id32',
        ]

        read_only_fields = ['id32']
class CustomerListSerializer(serializers.ModelSerializer):
    omzet = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()
    margin = serializers.SerializerMethodField()
    margin_percent = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'store_name', 'contact_number',
                  'address', 'omzet', 'qty', 'margin', 'margin_percent']
    
    def _get_order_items(self):
        return self.context.get('order_items')

    def get_omzet(self, obj):
        order_items = self._get_order_items()
        if not order_items:
            return

        total_omzet = order_items.aggregate(total_omzet=Sum(
            F('price') * F('quantity'))).get("total_omzet")
        return total_omzet if total_omzet else 0

    def get_qty(self, obj):
        order_items = self._get_order_items()
        if not order_items:
            return
        total_qty = order_items.aggregate(
            total_qty=Sum('quantity')).get("total_qty")
        return total_qty if total_qty else 0

    def get_margin(self, obj):
        order_items = self._get_order_items()
        if not order_items:
            return
        margin_amount = order_items.aggregate(margin=Sum(
            F('price') * F('quantity')) - Sum(F('product__base_price') * F('quantity'))).get('margin')
        margin_amount = 0 if not margin_amount else margin_amount
        return margin_amount

    def get_margin_percent(self, obj):
        total_omzet = self.get_omzet(obj)
        total_margin = self.get_margin(obj)

        try:
            return round(total_margin/total_omzet * 100, 2)
        except:
            return 0

class CustomerLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'store_name', 'payment_type',
                  'contact_number', 'address', 'location_coordinate']

class CustomerMapSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ['id32', 'location_coordinate', 'name']

    def get_location_coordinate(self, obj):
        """
        Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute.
        """
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None