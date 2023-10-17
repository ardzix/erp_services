from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from inventory.models import Product
from ..models import PurchaseOrder, PurchaseOrderItem, Supplier

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


# PurchaseOrder Serializer
# Simple serializer for list views
class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(slug_field='id32', queryset=Supplier.objects.all())
    supplier_name = serializers.StringRelatedField(source='supplier.name', read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ['id32', 'supplier', 'supplier_name', 'order_date', 'is_approved']
        read_only_fields = ['id32', 'is_approved']

# Nested serializer for detail and create views
class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(slug_field='id32', queryset=Supplier.objects.all())
    supplier_name = serializers.StringRelatedField(source='supplier.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, source='purchaseorderitem_set')

    class Meta:
        model = PurchaseOrder
        fields = ['id32', 'supplier', 'supplier_name', 'order_date', 'items', 'is_approved']
        read_only_fields = ['id32', 'is_approved']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('purchaseorderitem_set')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseOrderItem.objects.create(created_by=purchase_order.created_by, purchase_order=purchase_order, **item_data)

        return purchase_order
