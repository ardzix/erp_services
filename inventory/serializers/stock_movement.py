from urllib import request
from pkg_resources import require
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from inventory.views import stock_movement
from libs.utils import validate_file_by_id32
from purchasing.models import PurchaseOrderItem
from sales.models import SalesOrder
from ..models import StockMovement, StockMovementItem, Product, Unit, ProductLocation


class StockMovementSerializerMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Dynamically serialize the content object associated with origin
        if instance.origin:
            representation['origin'] = self.serialize_content_object(
                instance.origin)

        # Dynamically serialize the content object associated with destination
        if instance.destination:
            representation['destination'] = self.serialize_content_object(
                instance.destination)

        return representation

    def serialize_content_object(self, obj):
        return {
            "id32": obj.id32,
            "name": str(obj)
        }


class SMProductLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLocation
        fields = [
            'area',
            'shelving',
            'position'
        ]
        read_only_fields = ['id32']


class StockMovementItemListSerializer(serializers.ModelSerializer):
    def update(self, instances, validated_data):
        # Maps for id->instance and id->data item.
        item_mapping = {item.id32: item for item in instances}
        data_mapping = {item['id32']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for item_id, data in data_mapping.items():
            item = item_mapping.get(item_id, None)
            if item is not None:
                ret.append(self.child.update(item, data))

        return ret
    class Meta:
        model = StockMovementItem
        fields = ['id32', 'product', 'quantity', 'unit', 'buy_price',
                  'origin_movement_status', 'destination_movement_status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = {
            'id32': instance.product.id32,
            'name': instance.product.name,
            'sku': instance.product.sku
        }
        representation['unit'] = {
            'id32': instance.unit.id32,
            'symbol': instance.unit.symbol
        }

        origin_movement_status_dict = dict(StockMovementItem.STATUS_CHOICES)
        representation['origin_movement_status'] = {
            'key': instance.origin_movement_status,
            'value': origin_movement_status_dict.get(instance.origin_movement_status, ""),
        }

        destination_movement_status_dict = dict(
            StockMovementItem.STATUS_CHOICES)
        representation['destination_movement_status'] = {
            'key': instance.destination_movement_status,
            'value': destination_movement_status_dict.get(instance.destination_movement_status, ""),
        }
        return representation


class BatchSerializer(serializers.Serializer):
    id32 = serializers.CharField()
    expire_date = serializers.DateField()
    unit_symbol = serializers.CharField()
    quantity = serializers.IntegerField()


class StockMovementItemLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovementItem
        fields = ['id32', 'expire_date', 'origin_movement_status',
                  'destination_movement_status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        origin_movement_status_dict = dict(StockMovementItem.STATUS_CHOICES)
        representation['origin_movement_status'] = {
            'key': instance.origin_movement_status,
            'value': origin_movement_status_dict.get(instance.origin_movement_status, ""),
        }

        destination_movement_status_dict = dict(
            StockMovementItem.STATUS_CHOICES)
        representation['destination_movement_status'] = {
            'key': instance.destination_movement_status,
            'value': destination_movement_status_dict.get(instance.destination_movement_status, ""),
        }
        return representation


class StockMovementItemSerializer(serializers.ModelSerializer):
    product_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    unit_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Unit.objects.all(),
        source='unit',
        write_only=True
    )
    origin_locations = SMProductLocationSerializer(many=True, read_only=True)
    destination_locations = SMProductLocationSerializer(
        many=True, read_only=True)
    batches = serializers.SerializerMethodField()

    class Meta:
        model = StockMovementItem
        fields = ['id32', 'product', 'product_id32', 'quantity', 'unit', 'expire_date',
                  'unit_id32', 'order', 'origin_locations', 'destination_locations',
                  'buy_price',
                  'origin_movement_status', 'destination_movement_status', 'batches']
        read_only_fields = ['id32', 'stock_movement', 'product',
                            'unit', 'origin_locations', 'destination_locations']

    def get_batches(self, obj):
        return BatchSerializer(obj.batches, many=True).data

    def create(self, validated_data):
        # `SlugRelatedField` will automatically convert the 'id32' to the actual model instance for us.
        # So, we can pass `validated_data` directly to `StockMovementItem.objects.create()`.
        return StockMovementItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.product = validated_data.get('product', instance.product)
        instance.stock_movement = validated_data.get(
            'stock_movement', instance.stock_movement)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.unit = validated_data.get('unit', instance.unit)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.product:
            representation['product'] = {
                'id32': instance.product.id32,
                'str': instance.product.__str__()
            }
        if instance.unit:
            representation['unit'] = {
                'id32': instance.unit.id32,
                'str': instance.unit.__str__()
            }

        origin_movement_status_dict = dict(StockMovementItem.STATUS_CHOICES)
        representation['origin_movement_status'] = {
            'key': instance.origin_movement_status,
            'value': origin_movement_status_dict.get(instance.origin_movement_status, ""),
        }

        destination_movement_status_dict = dict(
            StockMovementItem.STATUS_CHOICES)
        representation['destination_movement_status'] = {
            'key': instance.destination_movement_status,
            'value': destination_movement_status_dict.get(instance.destination_movement_status, ""),
        }
        return representation


class StockMovementItemPOBatchSerializer(serializers.ModelSerializer):
    product_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Product.objects.all(),
        source='product'
    )
    po_item_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=PurchaseOrderItem.objects.all(),
        source='po_item'
    )

    class Meta:
        model = StockMovementItem
        fields = ['product_id32', 'po_item_id32', 'destination_movement_status', 'origin_movement_status',
                  'quantity', 'expire_date', 'buy_price', 'order']

    def save(self, **kwargs):
        # Extract stock_movement from context and set it to the instance before saving
        stock_movement = self.context.get('stock_movement')
        if stock_movement:
            self.validated_data['stock_movement'] = stock_movement
        self.validated_data['unit'] = self.validated_data.get(
            'product').purchasing_unit
        return super().save(**kwargs)


class StockMovementItemCreateSerializer(serializers.ModelSerializer):
    stock_movement_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=StockMovement.objects.all(),
        source='stock_movement',
        required=True
    )
    product_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Product.objects.all(),
        source='product'
    )
    unit_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Unit.objects.all(),
        source='unit'
    )

    class Meta:
        model = StockMovementItem
        fields = ('stock_movement_id32',
                  'product_id32',
                  'unit_id32',
                  'quantity',
                  'origin_movement_status',
                  'destination_movement_status',
                  'buy_price',
                  'expire_date')


class StockMovementItemUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockMovementItem
        fields = ('origin_movement_status',
                  'buy_price',
                  'destination_movement_status', 'expire_date', 'quantity')


class StockMovementListSerializer(StockMovementSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ['id32', 'created_at', 'origin',
                  'destination', 'movement_date', 'status']


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['model', 'app_label']


class StockMovementDetailSerializer(StockMovementSerializerMixin, serializers.ModelSerializer):
    items = StockMovementItemListSerializer(many=True, read_only=True)
    origin_type = ContentTypeSerializer(read_only=True)
    destination_type = ContentTypeSerializer(read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id32', 'created_at', 'origin', 'destination', 'origin_type',
                  'destination_type', 'movement_date', 'status', 'movement_evidence',
                  'items', 'last_purchase_order']
        read_only_fields = ['id32', 'created_at', 'last_purchase_order']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.movement_evidence:
            representation['movement_evidence'] = {
                'id32': instance.movement_evidence.id32,
                'url': instance.movement_evidence.file.url
            }
        if instance.last_purchase_order:
            representation['last_purchase_order'] = {
                'id32': instance.last_purchase_order.id32,
                'supplier': instance.last_purchase_order.supplier.__str__(),
            }
        return representation


class StockMovementCreateSerializer(serializers.ModelSerializer):
    origin_type = serializers.ChoiceField(
        choices=['warehouse', 'supplier', 'customer'], write_only=True)
    destination_type = serializers.ChoiceField(
        choices=['warehouse', 'supplier', 'customer'], write_only=True)
    origin_id32 = serializers.CharField(write_only=True)
    destination_id32 = serializers.CharField(write_only=True)
    movement_evidence_id32 = serializers.CharField(
        write_only=True, required=False)
    items = StockMovementItemSerializer(many=True, required=False)
    salesorder_id32s = serializers.ListField(required=False, write_only=True)

    class Meta:
        model = StockMovement
        fields = ['id32', 'created_at', 'status', 'movement_date', 'destination_type',
                  'destination_id32', 'origin_type', 'origin_id32', 'movement_evidence_id32',
                  'movement_evidence', 'items', 'salesorder_id32s', 'generate_items_from_sales']
        read_only_fields = ['id32', 'created_at', 'movement_evidence']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.movement_evidence:
            representation['movement_evidence'] = {
                'id32': instance.movement_evidence.id32,
                'url': instance.movement_evidence.file.url
            }
        return representation

    def validate_origin_type(self, value):
        content_type = ContentType.objects.filter(model=value).first()
        if not content_type:
            raise serializers.ValidationError({
                "origin_type": _("Invalid content type for origin.")
            })
        return content_type

    def validate_destination_type(self, value):
        content_type = ContentType.objects.filter(model=value).first()
        if not content_type:
            raise serializers.ValidationError({
                "destination_type": _("Invalid content type for destination.")
            })
        return content_type

    def validate_movement_evidence_id32(self, value):
        return validate_file_by_id32(value, "A file with id32 {value} does not exist for the movement evidence.")

    def validate(self, data):
        if "origin_id32" in data and "origin_type" in data:
            model_class = data["origin_type"].model_class()
            try:
                origin_instance = model_class.objects.get(
                    id32=data.pop("origin_id32"))
                data["origin_id"] = origin_instance.id
            except model_class.DoesNotExist:
                raise serializers.ValidationError({
                    "origin_id32": _("Invalid origin_id32 provided."),
                })

        if "destination_id32" in data and "destination_type" in data:
            model_class = data["destination_type"].model_class()
            try:
                destination_instance = model_class.objects.get(
                    id32=data.pop("destination_id32"))
                data["destination_id"] = destination_instance.id
            except model_class.DoesNotExist:
                raise serializers.ValidationError({
                    "destination_id32": _("Invalid destination_id32 provided."),
                })
        if 'salesorder_id32s' in data:
            sales_orders = SalesOrder.objects.filter(
                id32__in=data.get('salesorder_id32s'))
            if sales_orders.exists():
                items = data.get('items')
                items = [] if not items else items
                for order in sales_orders:
                    for item in order.order_items.all():
                        items.append({
                            'product': item.product,
                            'quantity': item.quantity,
                            'unit': item.unit,
                        })
                data['items'] = items

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        if 'salesorder_id32s' in validated_data:
            sales_orders = SalesOrder.objects.filter(
                id32__in=validated_data.pop('salesorder_id32s'))
        else:
            sales_orders = []
        movement_evidence = validated_data.pop(
            'movement_evidence_id32') if 'movement_evidence_id32' in validated_data else None
        validated_data['movement_evidence'] = movement_evidence
        stock_movement = StockMovement.objects.create(**validated_data)
        if stock_movement.generate_items_from_sales:
            for item_data in items_data:
                StockMovementItem.objects.create(
                    stock_movement=stock_movement, **item_data)
        for order in sales_orders:
            order.stock_movements.add(stock_movement)
        return stock_movement

    def update(self, instance, validated_data):
        if 'items' in validated_data:
            validated_data.pop('items')
        if 'movement_evidence_id32' in validated_data:
            movement_evidence = validated_data.pop('movement_evidence_id32')
            validated_data['movement_evidence'] = movement_evidence
        return super().update(instance, validated_data)


class DistinctStockMovementItemSerializer(serializers.Serializer):
    product_id32 = serializers.CharField(source='product__id32')
    product_name = serializers.CharField(source='product__name')
    unit_id32 = serializers.CharField(source='unit__id32')
    unit_name = serializers.CharField(source='unit__name')
    total_quantity = serializers.IntegerField()
    destination_locations = serializers.SerializerMethodField()
    origin_locations = serializers.SerializerMethodField()
    item_details = serializers.SerializerMethodField()

    class Meta:
        fields = ['product_id32', 'product_name', 'origin_locations',
                  'destination_locations', 'unit_id32', 'unit_name', 'total_quantity', 'item_details']

    def get_item_details(self, instance):
        queryset = StockMovementItem.objects.filter(
            stock_movement=instance.get('stock_movement'),
            product__id32=instance.get('product__id32'),
            unit__id32=instance.get('unit__id32'))
        return StockMovementItemLiteSerializer(queryset, many=True).data

    def stock_movement(self, instance):
        return StockMovement.objects.get(id=instance.get('stock_movement'))

    def get_origin_locations(self, instance):
        stock_movement = self.stock_movement(instance)
        if not stock_movement.origin or stock_movement.origin_type.model != 'warehouse':
            return []
        return SMProductLocationSerializer(ProductLocation.objects.filter(warehouse=stock_movement.origin, product__id32=instance.get('product__id32')), many=True).data

    def get_destination_locations(self, instance):
        stock_movement = self.stock_movement(instance)
        if not stock_movement.destination or stock_movement.destination_type.model != 'warehouse':
            return []
        return SMProductLocationSerializer(ProductLocation.objects.filter(warehouse=stock_movement.destination, product__id32=instance.get('product__id32')), many=True).data




class StockMovementItemBulkUpdateSerializer(serializers.Serializer):
    id32 = serializers.CharField()
    origin_movement_status = serializers.CharField(required=False)
    destination_movement_status = serializers.CharField(required=False)
    expire_date = serializers.DateField(required=False)
    quantity = serializers.IntegerField(required=False)

    class Meta:
        list_serializer_class = StockMovementItemListSerializer

    def update(self, instance, validated_data):
        instance.origin_movement_status = validated_data.get(
            'origin_movement_status', instance.origin_movement_status)
        instance.destination_movement_status = validated_data.get(
            'destination_movement_status', instance.destination_movement_status)
        instance.expire_date = validated_data.get(
            'expire_date', instance.expire_date)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance
