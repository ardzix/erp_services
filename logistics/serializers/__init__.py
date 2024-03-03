from rest_framework import serializers
from inventory.models import Warehouse
from libs.serializers import UsernamesField, User
from ..models import Vehicle, Driver

class DriverSerializer(serializers.ModelSerializer):
    username = UsernamesField(
        source='owned_by', many=False,  required=False, queryset=User.objects.all())
    class Meta:
        model = Driver
        fields = ['id32', 'name', 'phone_number', 'device_gps', 'username']
        read_only_fields = ['id32']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['vehicles'] = VehicleListSerializer(instance.vehicles.all(), many=True).data
        return representation

class VehicleSerializer(serializers.ModelSerializer):
    driver_id32 = serializers.CharField(write_only=True)
    warehouse_id32 = serializers.CharField(write_only=True)

    class Meta:
        model = Vehicle
        fields = ['id32', 'name', 'driver_id32', 'driver', 'license_plate', 'warehouse_id32', 'warehouse']
        read_only_fields = ['id32', 'driver', 'warehouse']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['driver'] = {
            'id32': instance.driver.id32 if instance.driver else None,
            'name': instance.driver.name if instance.driver else None
        }
        
        representation['warehouse'] = {
            'id32': instance.warehouse.id32 if instance.warehouse else None,
            'name': instance.warehouse.name if instance.warehouse else None
        }
        
        return representation

    def create(self, validated_data):
        driver_id32 = validated_data.pop('driver_id32', None)
        warehouse_id32 = validated_data.pop('warehouse_id32', None)

        if driver_id32:
            validated_data['driver'] = Driver.objects.get(id32=driver_id32)
        if warehouse_id32:
            validated_data['warehouse'] = Warehouse.objects.get(id32=warehouse_id32)
            
        return super(VehicleSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        driver_id32 = validated_data.pop('driver_id32', None)
        warehouse_id32 = validated_data.pop('warehouse_id32', None)

        if driver_id32:
            instance.driver = Driver.objects.get(id32=driver_id32)
        if warehouse_id32:
            instance.warehouse = Warehouse.objects.get(id32=warehouse_id32)

        return super(VehicleSerializer, self).update(instance, validated_data)


class VehicleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id32', 'name']
