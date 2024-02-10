from rest_framework import serializers
from django.core.exceptions import ValidationError
from inventory.models import Product, Warehouse
from hr.models import Employee
from ..models import ProductionOrder, WorkOrder, ProductionTracking, BOMComponent, BillOfMaterials

class ProductionOrderSerializer(serializers.ModelSerializer):
    components = serializers.SerializerMethodField()
    product_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = ProductionOrder
        fields = ['id32', 'product_id32','product', 'quantity', 'start_date', 'end_date', 'components']
        read_only_fields = ['id32', 'product']

    def get_components(self, obj):
        bom = BillOfMaterials.objects.filter(products=obj.product).first()
        if bom:
            components = BOMComponent.objects.filter(bom=bom)
            return ', '.join([f'{component.component.name}: {component.quantity}pcs' for component in components])
        return ''

class WorkOrderSerializer(serializers.ModelSerializer):
    quantity = serializers.ReadOnlyField(source='production_order.quantity')
    production_order_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=ProductionOrder.objects.all(),
        source='production_order',
        write_only=True
    )
    work_center_warehouse_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Warehouse.objects.all(),
        source='work_center_warehouse',
        write_only=True
    )
    employee_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Employee.objects.all(),
        source='assigned_to',
        write_only=True
    )

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


    class Meta:
        model = WorkOrder
        fields = ['id32', 'production_order_id32', 'production_order', 'operation_number', 'work_center', 'work_center_warehouse_id32', 'work_center_warehouse', 'employee_id32', 'assigned_to', 'start_time', 'end_time', 'quantity']
        read_only_fields = ['id32', 'production_order', 'work_center_warehouse' ,'assigned_to']

class ProductionTrackingSerializer(serializers.ModelSerializer):
    work_order_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=WorkOrder.objects.all(),
        source='work_order',
        write_only=True
    )

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
    class Meta:
        model = ProductionTracking
        fields = ['id32', 'work_order_id32', 'work_order', 'start_time', 'end_time', 'produced_quantity']
        read_only_fields = ['id32', 'work_order']
