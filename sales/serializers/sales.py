from rest_framework import serializers
from django.db.models import F, Sum
from common.serializers import UserListSerializer
from .customer import CustomerLiteSerializer
from inventory.models import Product
from ..models import SalesOrder, OrderItem, Customer

class OrderItemSerializer(serializers.ModelSerializer):
    product_id32 = serializers.CharField(source='product.id32')
    
    class Meta:
        model = OrderItem
        fields = ['id32', 'product_id32', 'quantity', 'price']
        read_only_fields = ['id32']

    def validate_product_id32(self, value):
        try:
            Product.objects.get(id32=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product with this id32 does not exist.")

    def to_representation(self, instance):
        """Override to represent product as its id32."""
        representation = super().to_representation(instance)
        representation['product_id32'] = instance.product.id32
        return representation

class SalesOrderListSerializer(serializers.ModelSerializer):
    approved_by = serializers.CharField(
        source='approved_by.email',
        read_only=True
    )
    customer = serializers.CharField(
        source='customer.name',
        read_only=True
    )
    total_amount = serializers.SerializerMethodField()
    class Meta:
        model = SalesOrder
        fields = ['id32', 'customer', 'order_date', 'approved_by', 'total_amount']
        read_only_fields = ['id32', 'approved_by', 'customer']

    def get_total_amount(self, obj):
        total_amount = obj.order_items.aggregate(total_price=Sum(F('price') * F('quantity'))).get('total_price')
        total_amount = 0 if not total_amount else total_amount
        return total_amount


class SalesOrderDetailSerializer(SalesOrderListSerializer):
    order_items = OrderItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()
    approved_by = UserListSerializer(read_only=True)
    customer = CustomerLiteSerializer(read_only=True)
    delivery_status = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrder
        fields = ['id32', 'customer', 'order_date', 'approved_by', 'total_amount', 'order_items', 'delivery_status']
        read_only_fields = ['id32', 'approved_by', 'customer', 'delivery_status']
    
    def get_delivery_status(self, obj):
        return obj.delivery_status


class SalesOrderSerializer(SalesOrderListSerializer):
    order_items = OrderItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()
    customer_id32 = serializers.CharField(write_only=True)  # Add the customer_id32 field


    class Meta:
        model = SalesOrder
        fields = ['id32', 'customer_id32', 'order_date', 'total_amount', 'order_items']
        read_only_fields = ['id32']

    def validate_customer_id32(self, value):
        """
        Validate the customer_id32 field, ensuring a Customer object with this ID exists.
        """
        try:
            # Assign the customer object to the validated data directly
            customer = Customer.objects.get(id32=value)
            return customer  # We are returning the customer object instead of id32
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"A customer with id32 {value} does not exist.")

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        customer = validated_data.pop('customer_id32')
        validated_data['customer'] = customer
        sales_order = SalesOrder.objects.create(**validated_data)

        for item_data in order_items_data:
            product = item_data.pop('product', None)
            product_instance = Product.objects.get(id32=product.get('id32'))
            # Add the actual product to the item_data
            item_data['product'] = product_instance
            OrderItem.objects.create(order=sales_order, created_by=sales_order.created_by, **item_data)

        return sales_order
    
    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items', None)

        # Update the SalesOrder fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if not order_items_data:
            return instance

        # Handle the nested OrderItems
        existing_order_items = OrderItem.objects.filter(order=instance)

        # Remove OrderItems not present in the provided data
        existing_ids = set(existing_order_items.values_list('id', flat=True))
        provided_ids = {item.get('id') for item in order_items_data if 'id' in item}
        to_delete_ids = existing_ids - provided_ids
        OrderItem.objects.filter(id__in=to_delete_ids).delete()
        # Create new or update existing OrderItems
        for item_data in order_items_data:
            # Obtain product from product_id32 and remove it from item_data
            product = item_data.pop('product', None)
            product_instance = Product.objects.get(id32=product.get('id32'))
            # Add the actual product to the item_data
            item_data['product'] = product_instance
            if 'id' in item_data:
                order_item_id = item_data.pop('id')
                OrderItem.objects.filter(id=order_item_id).update(**item_data)
            else:
                OrderItem.objects.create(order=instance, created_by = instance.created_by, **item_data)

        return instance

