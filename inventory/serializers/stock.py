from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from ..models import WarehouseStock, Warehouse, Product, Unit, StockMovementItem


class WarehouseStockSerializer(serializers.ModelSerializer):
    warehouse_id32 = serializers.CharField(write_only=True)
    product_id32 = serializers.CharField(write_only=True)
    unit_id32 = serializers.CharField(write_only=True)
    inbound_movement_item_id32 = serializers.CharField(
        write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = WarehouseStock
        fields = [
            'id32', 'warehouse_id32', 'warehouse', 'product_id32', 'product',
            'quantity', 'expire_date', 'inbound_movement_item_id32', 'inbound_movement_item',
            'dispatch_movement_items', 'unit_id32', 'unit'
        ]
        read_only_fields = ['id32', 'warehouse', 'product',
                            'inbound_movement_item', 'dispatch_movement_items', 'unit']

    def validate_warehouse_id32(self, value):
        try:
            Warehouse.objects.get(id32=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                _("Provided warehouse_id32 does not match any Warehouse records."))
        return value

    def validate_product_id32(self, value):
        try:
            Product.objects.get(id32=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                _("Provided product_id32 does not match any Product records."))
        return value

    def validate_unit_id32(self, value):
        try:
            Unit.objects.get(id32=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                _("Provided unit_id32 does not match any Unit records."))
        return value

    def validate_inbound_movement_item_id32(self, value):
        try:
            StockMovementItem.objects.get(id32=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                _("Provided inbound_movement_item_id32 does not match any StockMovementItem records."))
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['warehouse'] = {
            'id32': instance.warehouse.id32,
            'name': instance.warehouse.name
        }
        representation['product'] = {
            'id32': instance.product.id32,
            'name': instance.product.name
        }
        representation['unit'] = {
            'id32': instance.unit.id32,
            'name': instance.unit.name
        }
        if instance.inbound_movement_item:
            representation['inbound_movement_item'] = {
                'id32': instance.inbound_movement_item.id32
            }
        return representation

    def create(self, validated_data):
        warehouse_id32 = validated_data.pop('warehouse_id32', None)
        product_id32 = validated_data.pop('product_id32', None)
        unit_id32 = validated_data.pop('unit_id32', None)
        inbound_movement_item_id32 = validated_data.pop(
            'inbound_movement_item_id32', None)

        if warehouse_id32:
            validated_data['warehouse'] = Warehouse.objects.get(
                id32=warehouse_id32)
        if product_id32:
            validated_data['product'] = Product.objects.get(id32=product_id32)
        if unit_id32:
            validated_data['unit'] = Unit.objects.get(id32=unit_id32)
        if inbound_movement_item_id32:
            validated_data['inbound_movement_item'] = StockMovementItem.objects.get(
                id32=inbound_movement_item_id32)

        return super(WarehouseStockSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        warehouse_id32 = validated_data.pop('warehouse_id32', None)
        product_id32 = validated_data.pop('product_id32', None)
        unit_id32 = validated_data.pop('unit_id32', None)
        inbound_movement_item_id32 = validated_data.pop(
            'inbound_movement_item_id32', None)

        if warehouse_id32:
            instance.warehouse = Warehouse.objects.get(id32=warehouse_id32)
        if product_id32:
            instance.product = Product.objects.get(id32=product_id32)
        if unit_id32:
            instance.unit = Unit.objects.get(id32=unit_id32)
        if inbound_movement_item_id32:
            instance.inbound_movement_item = StockMovementItem.objects.get(
                id32=inbound_movement_item_id32)

        return super(WarehouseStockSerializer, self).update(instance, validated_data)


class DistinctWarehouseStockSerializer(serializers.Serializer):
    warehouse__id32 = serializers.CharField()
    warehouse__name = serializers.CharField()
    product__id32 = serializers.CharField()
    product__name = serializers.CharField()
    unit__id32 = serializers.CharField()
    unit__name = serializers.CharField()
    unit__symbol = serializers.CharField()
    total_quantity = serializers.IntegerField()
    price = serializers.SerializerMethodField()

    def get_price(self, instance):
        unit = Unit.objects.filter(id32=instance.get('unit__id32')).last()
        product = Product.objects.filter(id32=instance.get('product__id32')).last()
        if unit and product:
            return unit.conversion_to_top_level() * product.sell_price
        else:
            return None
