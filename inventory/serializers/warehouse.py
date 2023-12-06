from rest_framework import serializers
from django.contrib.gis.geos import Point
from libs.utils import handle_location
from ..models import Warehouse

class WarehouseSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = ['id32', 'name', 'type', 'address', 'location', 'location_coordinate']
        read_only_fields = ['id32']

    def get_location_coordinate(self, obj):
        """Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute."""
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    def create(self, validated_data):
        """Overrides the default create method to handle location before creating an instance."""
        validated_data = handle_location(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Overrides the default update method to handle location before updating an instance."""
        validated_data = handle_location(validated_data)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        type_dict = dict(Warehouse.TYPE_CHOICES)
        representation['type'] = {
            'key': instance.type,
            'value': type_dict.get(instance.type, ""),
        }

        return representation


class WarehouseListSerializer(WarehouseSerializer):

    class Meta:
        model = Warehouse
        fields = ['id32', 'name', 'type']
        read_only_fields = ['id32']