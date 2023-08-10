from rest_framework import serializers
from common.serializers import FileSerializer
from ..models import Product

class ProductListSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id32', 'name', 'sku', 'base_price', 'sell_price', 'quantity', 'product_type', 'picture']

    def get_picture(self, object):
        return object.picture.file.url if object.picture and object.picture.file else None

class ProductDetailSerializer(serializers.ModelSerializer):
    picture = FileSerializer(read_only=True)
    category = serializers.StringRelatedField()
    smallest_unit = serializers.StringRelatedField()
    purchasing_unit = serializers.StringRelatedField()
    sales_unit = serializers.StringRelatedField()
    stock_unit = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'base_price', 'sell_price', 
            'category', 'quantity', 'smallest_unit', 'purchasing_unit', 'sales_unit', 
            'stock_unit', 'product_type', 'price_calculation', 'brand', 'minimum_quantity', 
            'is_active', 'picture'
            # add or remove fields as needed
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        product_type_dict = dict(Product.PRODUCT_TYPE_CHOICES)
        price_calculation_dict = dict(Product.PRICE_CALCULATION)

        representation['product_type'] = product_type_dict.get(instance.product_type, "")
        representation['price_calculation'] = price_calculation_dict.get(instance.price_calculation, "")
        
        return representation

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'base_price', 'sell_price', 'category', 'quantity', 'smallest_unit', 'product_type', 'price_calculation']

class ProductEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'description', 'base_price', 'sell_price', 
            'category', 'quantity', 'smallest_unit', 'purchasing_unit', 'sales_unit', 
            'stock_unit', 'product_type', 'price_calculation', 'brand', 'minimum_quantity', 
            'is_active'
            # add or remove fields as needed
        ]
