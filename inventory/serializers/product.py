from rest_framework import serializers
from common.serializers import FileSerializer
from purchasing.serializers.supplier import SupplierProductSerializer
from purchasing.models import SupplierProduct
from ..models import Product


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


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id32', 'name', 'sku', 'category',
                  'smallest_unit', 'product_type', 'price_calculation']
        read_only_fields = ['id32']


class ProductEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'base_price', 'sell_price',
            'margin_type', 'margin_value',
            'category', 'quantity', 'smallest_unit', 'purchasing_unit', 'sales_unit',
            'stock_unit', 'product_type', 'price_calculation', 'brand', 'minimum_quantity',
            'is_active'
            # add or remove fields as needed
        ]
