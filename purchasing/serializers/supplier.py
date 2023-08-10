from rest_framework import serializers
from ..models import Supplier
from identities.models import CompanyProfile


class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id32', 'name', 'company_profile']


class SupplierDetailSerializer(serializers.ModelSerializer):
    company_profile = serializers.PrimaryKeyRelatedField(queryset=CompanyProfile.objects.all())
    location_coordinate = serializers.SerializerMethodField()

    def get_location_coordinate(self, obj):
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    class Meta:
        model = Supplier
        fields = [
            'id32', 'name', 'contact_number', 'address', 'location', 
            'location_coordinate', 'company_profile'
        ]


class SupplierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_number', 'address', 'company_profile']


class SupplierEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_number', 'address', 'location', 
            'company_profile'
        ]
