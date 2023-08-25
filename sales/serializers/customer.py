from rest_framework import serializers
from django.contrib.gis.geos import Point
from ..models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()

    def get_location_coordinate(self, obj):
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    class Meta:
        model = Customer
        fields = ['id32', 'name', 'contact_number', 'address', 'location', 'location_coordinate', 'company_profile']

    def create(self, validated_data):
        # Convert the coordinates to a Point object
        location_data = validated_data.pop('location')
        longitude, latitude = location_data.split(',')
        validated_data['location'] = Point(float(longitude), float(latitude))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Convert the coordinates to a Point object
        location_data = validated_data.pop('location')
        longitude, latitude = location_data.split(',')
        validated_data['location'] = Point(float(longitude), float(latitude))
        return super().update(instance, validated_data)
    
class CustomerLiteSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'contact_number', 'address', 'location_coordinate']

#e920477217b35578fa1e71f7aa5b280771987b13