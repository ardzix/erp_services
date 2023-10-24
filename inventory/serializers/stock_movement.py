from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
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
    class Meta:
        model = StockMovementItem
        fields = ['id32', 'product', 'quantity', 'unit']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.name
        representation['unit'] = instance.unit.symbol
        return representation


class BatchSerializer(serializers.Serializer):
    id32 = serializers.CharField()
    expire_date = serializers.DateField()
    unit_symbol = serializers.CharField()
    quantity = serializers.IntegerField()


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
                  'origin_movement_status', 'destination_movement_status', 'batches']
        read_only_fields = ['id32', 'stock_movement', 'product',
                            'unit', 'origin_locations', 'destination_locations',
                            'origin_movement_status', 'destination_movement_status']
        
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


class StockMovementItemUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockMovementItem
        fields = ('origin_movement_status',
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
                  'destination_type', 'movement_date', 'status', 'items']
        read_only_fields = ['id32', 'created_at']


class StockMovementCreateSerializer(serializers.ModelSerializer):
    origin_type = serializers.ChoiceField(
        choices=['warehouse', 'supplier', 'customer'], write_only=True)
    destination_type = serializers.ChoiceField(
        choices=['warehouse', 'supplier', 'customer'], write_only=True)
    origin_id32 = serializers.CharField(write_only=True)
    destination_id32 = serializers.CharField(write_only=True)
    items = StockMovementItemSerializer(many=True)

    class Meta:
        model = StockMovement
        fields = ['id32', 'created_at', 'status', 'movement_date', 'destination_type',
                  'destination_id32', 'origin_type', 'origin_id32', 'items']
        read_only_fields = ['id32', 'created_at']

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

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        stock_movement = StockMovement.objects.create(**validated_data)
        for item_data in items_data:
            StockMovementItem.objects.create(
                stock_movement=stock_movement, **item_data)

        return stock_movement
