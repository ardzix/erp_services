from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from ..models import StockMovement, StockMovementItem

class StockMovementSerializerMixin:
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Dynamically serialize the content object associated with origin
        if instance.origin:
            representation['origin'] = self.serialize_content_object(instance.origin)

        # Dynamically serialize the content object associated with destination
        if instance.destination:
            representation['destination'] = self.serialize_content_object(instance.destination)

        return representation

    def serialize_content_object(self, obj):
        return {
            "id32": obj.id32,
            "name": str(obj)
        }

class StockMovementItemSerializer(serializers.ModelSerializer):
    product_id32 = serializers.CharField(source='product.id32', read_only=True)
    
    class Meta:
        model = StockMovementItem
        fields = ['id32', 'product', 'product_id32', 'quantity', 'buy_price']

class StockMovementListSerializer(StockMovementSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ['id32', 'origin', 'destination', 'movement_date', 'status']

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['model', 'app_label']

class StockMovementDetailSerializer(StockMovementSerializerMixin, serializers.ModelSerializer):
    items = StockMovementItemSerializer(many=True, read_only=True)
    origin_type = ContentTypeSerializer(read_only=True)
    destination_type = ContentTypeSerializer(read_only=True)
    
    class Meta:
        model = StockMovement
        fields = ['id', 'origin', 'destination', 'origin_type', 'destination_type', 'movement_date', 'status', 'items']


class StockMovementUpdateSerializer(serializers.ModelSerializer):
    origin_type = serializers.ChoiceField(choices=['warehouse', 'supplier', 'customer'], write_only=True)
    destination_type = serializers.ChoiceField(choices=['warehouse', 'supplier', 'customer'], write_only=True)
    origin_id32 = serializers.CharField(write_only=True)
    destination_id32 = serializers.CharField(write_only=True)


    class Meta:
        model = StockMovement
        fields = ['status', 'movement_date', 'destination_type', 'destination_id32', 'origin_type', 'origin_id32']

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
                origin_instance = model_class.objects.get(id32=data["origin_id32"])
                data["origin_id"] = origin_instance.id
            except model_class.DoesNotExist:
                raise serializers.ValidationError({
                    "origin_id32": _("Invalid origin_id32 provided."),
                })

        if "destination_id32" in data and "destination_type" in data:
            model_class = data["destination_type"].model_class()
            try:
                destination_instance = model_class.objects.get(id32=data["destination_id32"])
                data["destination_id"] = destination_instance.id
            except model_class.DoesNotExist:
                raise serializers.ValidationError({
                    "destination_id32": _("Invalid destination_id32 provided."),
                })

        return data