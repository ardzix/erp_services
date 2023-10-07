from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from identities.serializers import CompanyProfileSerializer
from inventory.models import Product
from identities.models import CompanyProfile
from ..models import Supplier, SupplierProduct


class CompanyProfileID32Mixin:
    def validate_company_profile_id32(self, value):
        if not CompanyProfile.objects.filter(id32=value).exists():
            raise serializers.ValidationError({
                "company_profile_id32": _("Invalid company profile ID32.")
            })
        return value

class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id32', 'name', 'company_profile']


class SupplierDetailSerializer(serializers.ModelSerializer):
    company_profile = CompanyProfileSerializer(read_only=True)
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


class SupplierCreateSerializer(CompanyProfileID32Mixin, serializers.ModelSerializer):
    company_profile_id32 = serializers.CharField(write_only=True, source="company_profile.id32", required=False)

    class Meta:
        model = Supplier
        fields = ['id32', 'name', 'contact_number', 'address', 'company_profile_id32']
        read_only_fields = ['id32']

    def create(self, validated_data):
        if 'company_profile' in validated_data:
            company_profile_id32 = validated_data.pop('company_profile')['id32']
            company_profile = CompanyProfile.objects.get(id32=company_profile_id32)
            validated_data['company_profile'] = company_profile
        return super().create(validated_data)


class SupplierEditSerializer(CompanyProfileID32Mixin, serializers.ModelSerializer):
    company_profile_id32 = serializers.CharField(write_only=True, source="company_profile.id32", required=False)

    class Meta:
        model = Supplier
        fields = [
            'id32', 'name', 'contact_number', 'address', 'location', 
            'company_profile_id32'
        ]
        read_only_fields = ['id32']

    def update(self, instance, validated_data):
        if 'company_profile' in validated_data:
            company_profile_id32 = validated_data.pop('company_profile')['id32']
            company_profile = CompanyProfile.objects.get(id32=company_profile_id32)
            validated_data['company_profile'] = company_profile
        return super().update(instance, validated_data)


class SupplierProductSerializer(serializers.ModelSerializer):
    id32 = serializers.CharField(read_only=True)
    supplier = serializers.CharField(write_only=True)  # Accept id32 for Supplier
    product = serializers.CharField(write_only=True)   # Accept id32 for Product
    supplier_name = serializers.StringRelatedField(source='supplier.name', read_only=True)
    product_name = serializers.StringRelatedField(source='product.name', read_only=True)

    class Meta:
        model = SupplierProduct
        fields = ['id32', 'supplier', 'supplier_name', 'product', 'product_name', 'is_default_supplier']

    def validate(self, data):

        if data.get('supplier'):
            try:
                Supplier.objects.get(id32=data['supplier'])
            except Supplier.DoesNotExist:
                raise serializers.ValidationError({'supplier':_("Supplier with this id32 does not exist.")})

        if data.get('product'):
            try:
                Product.objects.get(id32=data['product'])
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product':_("Product with this id32 does not exist.")})

        if data.get('product') and data.get('supplier') and SupplierProduct.objects.filter(supplier__id32=data['supplier'], product__id32=data['product']).exists():
            raise serializers.ValidationError({'product': _("A product with this supplier already exists.")})

        return data

    def create(self, validated_data):
        supplier = validated_data.pop('supplier')
        product = validated_data.pop('product')
        supplier_product = SupplierProduct.objects.create(supplier=supplier, product=product, **validated_data)
        return supplier_product


class BulkAddProductsSerializer(serializers.Serializer):
    supplier = serializers.CharField(write_only=True)  # Accept id32 for Supplier
    products = serializers.ListField(child=serializers.CharField())  # List of id32 for Products

    def validate_supplier(self, value):
        try:
            return Supplier.objects.get(id32=value)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError({'supplier':_("Supplier with this id32 does not exist.")})
    
    def validate_products(self, value):
        # Step 1: Check for duplicates within the incoming product list
        if len(value) != len(set(value)):
            raise serializers.ValidationError({'products':_("The product list contains duplicate entries.")})
        return value

    def validate(self, data):
        # Step 2: Check against the database for any existing combinations
        supplier = data['supplier']
        existing_products = SupplierProduct.objects.filter(
            supplier=supplier, 
            product__id32__in=data['products']
        )

        if existing_products.exists():
            existing_product_ids = existing_products.values_list('product__id32', flat=True)
            raise serializers.ValidationError(
                {'products':_("The supplier already has associations with product(s): {}").format(', '.join(existing_product_ids))}
            )
        return data