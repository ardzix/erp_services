from rest_framework import serializers
from inventory.models import Product
from ..models import BillOfMaterials, BOMProduct, BOMComponent
from .mixins import ComponentMixin


class BOMProductSerializer(ComponentMixin):
    class Meta:
        model = BOMProduct
        fields = ['id32', 'item_id32', 'item', 'unit_id32', 'unit', 'quantity']
        read_only_fields = ['id32', 'item', 'unit']


class BOMComponentSerializer(ComponentMixin):
    class Meta:
        model = BOMComponent
        fields = ['id32', 'item_id32', 'item', 'unit_id32', 'unit', 'quantity']
        read_only_fields = ['id32', 'item', 'unit']


class BillOfMaterialsSerializer(serializers.ModelSerializer):
    produced_from_bom = BOMProductSerializer(
        many=True, source='bomproduct_set', required=False)
    used_in_bom = BOMComponentSerializer(
        many=True, source='bomcomponent_set', required=False)

    class Meta:
        model = BillOfMaterials
        fields = ['id32', 'name', 'produced_from_bom', 'used_in_bom']
        read_only_fields = ['id32']

    def create(self, validated_data):
        # Pop related data from validated_data
        products_data = validated_data.pop('bomproduct_set', [])
        components_data = validated_data.pop('bomcomponent_set', [])

        # Create the BillOfMaterials instance
        bill_of_materials = BillOfMaterials.objects.create(**validated_data)

        # Create related BOMProduct and BOMComponent instances
        for product_data in products_data:
            BOMProduct.objects.create(bom=bill_of_materials, **product_data)
        for component_data in components_data:
            BOMComponent.objects.create(
                bom=bill_of_materials, **component_data)

        return bill_of_materials

    def update(self, instance, validated_data):
        # Pop related data from validated_data
        products_data = validated_data.pop('bomproduct_set', [])
        components_data = validated_data.pop('bomcomponent_set', [])

        # Update the BillOfMaterials instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle related BOMProduct and BOMComponent updates here
        # This could involve clearing existing relations and creating new ones,
        # or more complex logic to update existing instances without losing data.

        return instance
