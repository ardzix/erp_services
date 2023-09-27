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
            'store_type'
            ]
        read_only_fields = ['id32']
    


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.administrative_lv1:
            representation['administrative_lv1'] = {
                'id': instance.administrative_lv1.pk,
                'name': instance.administrative_lv1.name
            }
        if instance.administrative_lv2:
            representation['administrative_lv2'] = {
                'id': instance.administrative_lv2.pk,
                'name': instance.administrative_lv2.name
            }
        if instance.administrative_lv3:
            representation['administrative_lv3'] = {
                'id': instance.administrative_lv3.pk,
                'name': instance.administrative_lv3.name
            }
        if instance.administrative_lv4:
            representation['administrative_lv4'] = {
                'id': instance.administrative_lv4.pk,
                'name': instance.administrative_lv4.name
            }

        payment_type_dict = dict(Customer.PAYMENT_TYPE_CHOICES)
        store_type_dict = dict(Customer.STORE_TYPE_CHOICES)

        if instance.payment_type:
            representation['payment_type'] = {
                'key': instance.payment_type,
                'value': payment_type_dict.get(instance.payment_type, ""),
            }
        if instance.store_type:
            representation['store_type'] = {
                'key': instance.store_type,
                'value': store_type_dict.get(instance.store_type, ""),
            }

        return representation

    def create(self, validated_data):
        # Convert the coordinates to a Point object
        location_data = validated_data.pop('location')
        longitude, latitude = location_data.split(',')
        validated_data['location'] = Point(float(longitude), float(latitude))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Convert the coordinates to a Point object
        if 'location' in validated_data:
            location_data = validated_data.pop('location')
            longitude, latitude = location_data.split(',')
            validated_data['location'] = Point(float(longitude), float(latitude))
        return super().update(instance, validated_data)


class CustomerListSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'store_name', 'contact_number', 'address']


class CustomerLiteSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'store_name', 'contact_number', 'address', 'location_coordinate']

#e920477217b35578fa1e71f7aa5b280771987b13