from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from inventory.models import Product, Warehouse, Unit
from ..models import PurchaseOrder, PurchaseOrderItem, Supplier, InvalidPOItem

# PurchaseOrderItem Serializer
class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.StringRelatedField(source='product.name', read_only=True)
    product = serializers.SlugRelatedField(slug_field='id32', queryset=Product.objects.all())
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id32', 'product', 'product_name', 'quantity', 'po_price']
        read_only_fields = ['id32']

    def validate_product(self, product):
        if product.purchasing_unit is None:
            raise serializers.ValidationError({
                "product": _("The product's purchasing unit has not been set.")
            })
        return product

# InvalidPOItem Serializer
class InvalidPOItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(slug_field='id32', queryset=Product.objects.all(), required=False)
    unit = serializers.SlugRelatedField(slug_field='id32', queryset=Unit.objects.all(), required=False)
    purchase_order = serializers.SlugRelatedField(slug_field='id32', queryset=PurchaseOrder.objects.all(), required=False, write_only=True)
    
    class Meta:
        model = InvalidPOItem
        fields = ['id32', 'purchase_order', 'product', 'name', 'quantity', 'price', 'unit', 'discount']
        read_only_fields = ['id32']

# PurchaseOrder Serializer
# Simple serializer for list views
class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(slug_field='id32', queryset=Supplier.objects.all())
    supplier_name = serializers.StringRelatedField(source='supplier.name', read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ['id32', 'supplier', 'supplier_name', 'order_date', 'approval']
        read_only_fields = ['id32', 'approval']

# Nested serializer for detail and create views
class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(slug_field='id32', queryset=Supplier.objects.all())
    destination_warehouse = serializers.SlugRelatedField(slug_field='id32', queryset=Warehouse.objects.all(), required=False)
    supplier_name = serializers.StringRelatedField(source='supplier.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, source='purchaseorderitem_set')
    invalid_items = InvalidPOItemSerializer(many=True, source='invalidpoitem_set')

    class Meta:
        model = PurchaseOrder
        fields = ['id32', 'supplier', 'supplier_name', 'destination_warehouse', 'order_date', 'approval', 'items', 'invalid_items']
        read_only_fields = ['id32', 'approval']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('purchaseorderitem_set')
        invalid_items_data = validated_data.pop('invalidpoitem_set')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)

        return purchase_order
