from rest_framework import serializers
from django.contrib.gis.geos import Point
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

    def handle_location(self, validated_data):
        """Extracts and formats the location from the validated data."""
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            longitude, latitude = location_data.split(',')
            validated_data['location'] = Point(float(longitude), float(latitude))
        return validated_data

    def create(self, validated_data):
        """Overrides the default create method to handle location before creating an instance."""
        validated_data = self.handle_location(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Overrides the default update method to handle location before updating an instance."""
        validated_data = self.handle_location(validated_data)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        type_dict = dict(Warehouse.TYPE_CHOICES)
        representation['type'] = {
            'key': instance.type,
            'value': type_dict.get(instance.type, ""),
        }

        return representation
