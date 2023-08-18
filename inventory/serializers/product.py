from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from common.serializers import FileSerializer
from purchasing.serializers.supplier import SupplierProductSerializer
from purchasing.models import SupplierProduct
from ..models import Product, Category, Unit


class ProductValidator:

    def validate_category_id32(self, value):
        return self._validate_id32(value, 'category_id32', Category)

    def validate_smallest_unit_id32(self, value):
        return self._validate_id32(value, 'smallest_unit_id32', Unit)

    def validate_purchasing_unit_id32(self, value):
        if value:
            return self._validate_id32(value, 'purchasing_unit_id32', Unit)
        return None

    def validate_sales_unit_id32(self, value):
        if value:
            return self._validate_id32(value, 'sales_unit_id32', Unit)
        return None

    def validate_stock_unit_id32(self, value):
        if value:
            return self._validate_id32(value, 'stock_unit_id32', Unit)
        return None

    def _validate_id32(self, value, field_name, model_class):
        try:
            return model_class.objects.get(id32=value).id
        except model_class.DoesNotExist:
            raise serializers.ValidationError({field_name: _("Invalid {field} provided.").format(field=field_name)})

    def create(self, validated_data):
        self._map_id32_to_fk(validated_data, 'category_id32', 'category_id')
        self._map_id32_to_fk(validated_data, 'smallest_unit_id32', 'smallest_unit_id')
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        instance.category_id = validated_data.pop('category_id32', instance.category_id)
        instance.smallest_unit_id = validated_data.pop('smallest_unit_id32', instance.smallest_unit_id)
        instance.purchasing_unit_id = validated_data.pop('purchasing_unit_id32', instance.purchasing_unit_id)
        instance.sales_unit_id = validated_data.pop('sales_unit_id32', instance.sales_unit_id)
        instance.stock_unit_id = validated_data.pop('stock_unit_id32', instance.stock_unit_id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _map_id32_to_fk(self, validated_data, id32_key, fk_key):
        model_id = validated_data.pop(id32_key, None)
        if model_id:
            validated_data[fk_key] = model_id

class ProductListSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id32', 'name', 'sku', 'base_price',
                  'sell_price', 'quantity', 'product_type', 'picture']

    def get_picture(self, object):
        return object.picture.file.url if object.picture and object.picture.file else None


class SupplierSerializer(SupplierProductSerializer):
    supplier_product_id32 = serializers.StringRelatedField(
        source='id32', read_only=True)
    supplier_id32 = serializers.StringRelatedField(
        source='supplier.id32', read_only=True)
    supplier_name = serializers.StringRelatedField(
        source='supplier.name', read_only=True)

    class Meta:
        model = SupplierProduct
        fields = ['supplier_product_id32', 'supplier_id32',
                  'supplier_name', 'is_default_supplier']


class ProductDetailSerializer(serializers.ModelSerializer):
    picture = FileSerializer(read_only=True)
    category = serializers.StringRelatedField()
    smallest_unit = serializers.StringRelatedField()
    purchasing_unit = serializers.StringRelatedField()
    sales_unit = serializers.StringRelatedField()
    stock_unit = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    suppliers = SupplierSerializer(source='supplierproduct_set', many=True)

    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'last_buy_price', 'previous_buy_price', 'base_price', 'sell_price',
            'margin_type', 'margin_value',
            'category', 'quantity', 'smallest_unit', 'purchasing_unit', 'sales_unit',
            'stock_unit', 'product_type', 'price_calculation', 'brand', 'minimum_quantity',
            'is_active', 'picture', 'suppliers'
            # add or remove fields as needed
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        product_type_dict = dict(Product.PRODUCT_TYPE_CHOICES)
        price_calculation_dict = dict(Product.PRICE_CALCULATION_CHOICES)

        representation['product_type'] = product_type_dict.get(
            instance.product_type, "")
        representation['price_calculation'] = price_calculation_dict.get(
            instance.price_calculation, "")

        return representation


class ProductCreateSerializer(ProductValidator, serializers.ModelSerializer):
    category_id32 = serializers.CharField(write_only=True)
    smallest_unit_id32 = serializers.CharField(write_only=True)
    class Meta:
        model = Product
        fields = ['id32', 'name', 'sku', 'category_id32',
                  'smallest_unit_id32', 'product_type', 'price_calculation']
        read_only_fields = ['id32']


class ProductEditSerializer(ProductValidator, serializers.ModelSerializer):
    category_id32 = serializers.CharField(write_only=True)
    smallest_unit_id32 = serializers.CharField(write_only=True)
    purchasing_unit_id32 = serializers.CharField(write_only=True, required=False, allow_null=True, default=None)
    sales_unit_id32 = serializers.CharField(write_only=True, required=False, allow_null=True, default=None)
    stock_unit_id32 = serializers.CharField(write_only=True, required=False, allow_null=True, default=None)

    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'base_price', 'sell_price',
            'margin_type', 'margin_value',
            'category_id32', 'quantity', 'smallest_unit_id32', 'purchasing_unit_id32', 'sales_unit_id32',
            'stock_unit_id32', 'product_type', 'price_calculation', 'brand', 'minimum_quantity',
            'is_active'
            # add or remove fields as needed
        ]

    def validate(self, data):
        # Fetching the smallest_unit from either the validated_data or the instance (if it's not being updated)
        smallest_unit = Unit.objects.get(id=data.get('smallest_unit_id32', self.instance.smallest_unit_id if self.instance else None))
        
        # Now, for each of purchasing_unit, sales_unit, and stock_unit
        for unit_field in ['purchasing_unit_id32', 'sales_unit_id32', 'stock_unit_id32']:
            if unit_field in data:
                unit = Unit.objects.get(id=data[unit_field])
                if unit != smallest_unit:  # Only check ancestors if it's not the same as the smallest_unit
                    ancestors = unit.get_ancestors()

                    if smallest_unit not in ancestors:
                        raise serializers.ValidationError({
                            unit_field: _("The chosen unit does not have the smallest unit as an ancestor, nor is it the same as the smallest unit.")
                        })

        return data





