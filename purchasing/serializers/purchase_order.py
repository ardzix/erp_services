from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoCoreValidationError
from rest_framework import serializers
from libs.utils import validate_file_by_id32, handle_file_fields
from inventory.models import Product, Warehouse, Unit
from ..models import PurchaseOrder, PurchaseOrderItem, Supplier, InvalidPOItem

# PurchaseOrderItem Serializer


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.StringRelatedField(
        source='product.name', read_only=True)
    product = serializers.SlugRelatedField(
        slug_field='id32', queryset=Product.objects.all())

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
    product = serializers.SlugRelatedField(
        slug_field='id32', queryset=Product.objects.all(), required=False)
    unit = serializers.SlugRelatedField(
        slug_field='id32', queryset=Unit.objects.all(), required=False)
    purchase_order = serializers.SlugRelatedField(
        slug_field='id32', queryset=PurchaseOrder.objects.all(), required=False, write_only=True)

    class Meta:
        model = InvalidPOItem
        fields = ['id32', 'purchase_order', 'product',
                  'name', 'quantity', 'price', 'unit', 'discount']
        read_only_fields = ['id32']

# PurchaseOrder Serializer
# Simple serializer for list views


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(
        slug_field='id32', queryset=Supplier.objects.all())
    supplier_name = serializers.StringRelatedField(
        source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id32', 'supplier',
                  'supplier_name', 'order_date', 'approval',
                  'total']
        read_only_fields = ['id32', 'approval']

# Nested serializer for detail and create views


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SlugRelatedField(
        slug_field='id32', queryset=Supplier.objects.all())
    destination_warehouse = serializers.SlugRelatedField(
        slug_field='id32', queryset=Warehouse.objects.all(), required=False)
    supplier_name = serializers.StringRelatedField(
        source='supplier.name', read_only=True)
    items = PurchaseOrderItemSerializer(
        many=True, source='purchaseorderitem_set')
    invalid_items = InvalidPOItemSerializer(
        many=True, source='invalidpoitem_set', read_only=True)
    invalid_item_evidence_id32 = serializers.CharField(
        write_only=True, required=False)

    class Meta:
        model = PurchaseOrder
        fields = ['id32', 'supplier', 'supplier_name', 'destination_warehouse', 'order_date',
                  'approval', 'items', 'invalid_items', 'invalid_item_evidence_id32', 'invalid_item_evidence',
                  'discount_amount', 'tax_amount', 'subtotal', 'subtotal_after_discount', 'total']
        read_only_fields = ['id32', 'approval',
                            'invalid_items', 'invalid_item_evidence']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        file_fields = ['invalid_item_evidence']
        for field in file_fields:
            attr_instance = getattr(instance, field)
            if attr_instance:
                representation[field] = {
                    'id32': attr_instance.id32,
                    'url': attr_instance.file.url
                }
        if instance.destination_warehouse:
            representation['destination_warehouse'] = {
                'id32': instance.destination_warehouse.id32,
                'str': instance.destination_warehouse.__str__()
            }

        return representation

    def validate_invalid_item_evidence_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the visit evidence.")

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('purchaseorderitem_set')
        purchase_order = PurchaseOrder.objects.create(**validated_data)

        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order, **item_data)

        return purchase_order

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('purchaseorderitem_set', None)
        file_fields = {
            'invalid_item_evidence_id32': 'invalid_item_evidence'
        }
        validated_data = handle_file_fields(validated_data, file_fields)

        # Update the PurchaseOrder instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create PurchaseOrderItem instances
        if items_data is not None:
            existing_ids = [
                item.id for item in instance.purchaseorderitem_set.all()]
            for item_data in items_data:
                item_id = item_data.get('id', None)
                if item_id and item_id in existing_ids:
                    # Update existing item
                    PurchaseOrderItem.objects.filter(
                        id=item_id).update(**item_data)
                else:
                    # Create new item
                    PurchaseOrderItem.objects.create(
                        purchase_order=instance, **item_data)

            # Optional: remove items that are not in the updated data
            updated_ids = [item['id'] for item in items_data if 'id' in item]
            for item_id in existing_ids:
                if item_id not in updated_ids:
                    PurchaseOrderItem.objects.filter(id=item_id).delete()

        return instance


class PODownPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ("down_payment", "down_payment_date")
