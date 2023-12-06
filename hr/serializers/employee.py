# serializers.py

from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from libs.utils import handle_location
from ..models import Department, Employee, LocationTracker

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id32', 'name']
        read_only_fields = ['id32']

class EmployeeSerializer(serializers.ModelSerializer):
    department_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Department.objects.all(),
        source='department',
        required=False
    )
    user_username = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        source='user'
    )
    user_full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    last_location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ('id32', 'user_username', 'department_id32', 'user_full_name', 'department_name', 'last_location_coordinate')
        read_only_fields = ['id32', 'user_full_name', 'department_name']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_last_location_coordinate(self, obj):
        """
        Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute.
        """
        if obj.last_location:
            return {
                'latitude': obj.last_location.y,
                'longitude': obj.last_location.x
            }
        return None
    

class LocationTrackerSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()
    class Meta:
        model = LocationTracker
        fields = ['id32', 'employee', 'location', 'location_coordinate', 'created_at']
        read_only_fields = ['id32', 'employee', 'created_at']

    def create(self, validated_data):
        validated_data = handle_location(validated_data)
        return super().create(validated_data)

    def get_location_coordinate(self, obj):
        """Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute."""
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None