from rest_framework import serializers
from inventory.models import Product, Unit

class ComponentMixin(serializers.ModelSerializer):
    item_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Product.objects.all(),
        source='item',
        write_only=True
    )
    unit_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Unit.objects.all(),
        source='unit',
        write_only=True
    )
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        if instance.item:
            to_representation["item"] = {
                "id32": instance.item.id32,
                "str": instance.item.__str__(),
            }
        if instance.unit:
            to_representation["unit"] = {
                "id32": instance.unit.id32,
                "symbol": instance.unit.symbol,
            }
        return to_representation