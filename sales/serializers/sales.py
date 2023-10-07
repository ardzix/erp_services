from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from common.serializers import UserListSerializer
from common.models import File
from inventory.models import Product, Unit
from .customer import CustomerLiteSerializer
from ..models import SalesOrder, OrderItem, Customer, Invoice, SalesPayment


class OrderItemSerializer(serializers.ModelSerializer):
    product_id32 = serializers.CharField(source='product.id32')
    unit_id32 = serializers.CharField(source='unit.id32')

    class Meta:
        model = OrderItem
        fields = ['id32', 'product_id32', 'unit_id32', 'quantity', 'price']
        read_only_fields = ['id32']

    def validate(self, data):
        validated_data = super().validate(data)
        try:
            product = Product.objects.get(
                id32=validated_data.get('product')['id32'])

        except Product.DoesNotExist:
            raise serializers.ValidationError(
                {"product_id32": "Product with this id32 does not exist."})
        product_units_ids = list(product.smallest_unit.get_ancestors().values_list(
            'id', flat=True)) + list(product.smallest_unit.get_descendants().values_list('id', flat=True)) + [
                product.smallest_unit.id
        ]
        try:
            Unit.objects.get(id32=validated_data.get(
                'unit')['id32'], id__in=product_units_ids)
        except Unit.DoesNotExist:
            raise serializers.ValidationError(
                {"unit_id32": "Unit with this id32 does not exist or not suits with the product."})

        return validated_data

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
        fields = ['id32', 'customer', 'order_date',
                  'approved_by', 'total_amount', 'status']
        read_only_fields = ['id32', 'approved_by', 'customer']

    def get_total_amount(self, obj):
        total_amount = obj.order_items.aggregate(
            total_price=Sum(F('price') * F('quantity'))).get('total_price')
        total_amount = 0 if not total_amount else total_amount
        return total_amount


class SalesOrderDetailSerializer(SalesOrderListSerializer):
    order_items = OrderItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()
    approved_by = UserListSerializer(read_only=True)
    customer = CustomerLiteSerializer(read_only=True)

    class Meta:
        model = SalesOrder
        fields = ['id32', 'customer', 'order_date', 'approved_by',
                  'total_amount', 'order_items', 'delivery_status', 'status', 'invoice']
        read_only_fields = ['id32', 'approved_by',
                            'customer', 'delivery_status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        status_type_dict = dict(SalesOrder.STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_type_dict.get(instance.status, ""),
        }

        if instance.invoice:
            representation['invoice'] = {
                'id32': instance.invoice.id32,
                'str': instance.invoice.__str__()
            }
        return representation


class SalesOrderSerializer(SalesOrderListSerializer):
    order_items = OrderItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()
    customer_id32 = serializers.CharField(
        write_only=True)  # Add the customer_id32 field

    class Meta:
        model = SalesOrder
        fields = ['id32', 'customer_id32',
                  'order_date', 'total_amount', 'order_items']
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
            raise serializers.ValidationError(
                f"A customer with id32 {value} does not exist.")

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

            unit = item_data.pop('unit', None)
            unit_instance = Unit.objects.get(id32=unit.get('id32'))
            # Add the actual product to the item_data
            item_data['unit'] = unit_instance
            OrderItem.objects.create(
                order=sales_order, created_by=sales_order.created_by, **item_data)

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
        provided_ids = {item.get('id')
                        for item in order_items_data if 'id' in item}
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
                OrderItem.objects.create(
                    order=instance, created_by=instance.created_by, **item_data)

        return instance


class InvoiceSerializer(serializers.ModelSerializer):
    order_id32 = serializers.CharField(source='order.id32', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    vat_display = serializers.SerializerMethodField(method_name='get_vat_display')

    class Meta:
        model = Invoice
        fields = [
            'id32', 'order_id32', 'invoice_date', 'approved_by_username',
            'approved_at', 'vat', 'vat_display', 'payment_status'
        ]

    def get_vat_display(self, obj):
        return f"{obj.vat * 100:.2f}%"

    def validate_order_id32(self, value):
        try:
            order = SalesOrder.objects.get(id32=value)
            return order
        except SalesOrder.DoesNotExist:
            raise serializers.ValidationError(
                _("Order with this id32 does not exist."))

    def create(self, validated_data):
        order_id32 = validated_data.pop('order_id32', None)
        if order_id32:
            validated_data['order'] = SalesOrder.objects.get(id32=order_id32)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        order_id32 = validated_data.pop('order_id32', None)
        if order_id32:
            instance.order = SalesOrder.objects.get(id32=order_id32)
        return super().update(instance, validated_data)


class SalesPaymentSerializer(serializers.ModelSerializer):
    invoice_id32 = serializers.CharField(write_only=True)
    payment_evidence_id32 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SalesPayment
        fields = [
            'id32', 'invoice_id32', 'invoice', 'amount', 'payment_date',
            'payment_evidence_id32', 'payment_evidence', 'status'
        ]
        read_only_fields = ['id32', 'invoice', 'payment_evidence']

    def validate_invoice_id32(self, value):
        try:
            Invoice.objects.get(id32=value)
            return value
        except Invoice.DoesNotExist:
            raise serializers.ValidationError(
                _("Invoice with this id32 does not exist."))

    def validate_payment_evidence_id32(self, value):
        try:
            File.objects.get(id32=value)
            return value
        except File.DoesNotExist:
            raise serializers.ValidationError(
                _("File with this id32 does not exist."))

    def create(self, validated_data):
        invoice_id32 = validated_data.pop('invoice_id32', None)
        if invoice_id32:
            validated_data['invoice'] = Invoice.objects.get(id32=invoice_id32)
        file_id32 = validated_data.pop('payment_evidence_id32', None)
        if file_id32:
            validated_data['payment_evidence'] = File.objects.get(id32=invoice_id32)
        return super().create(validated_data)

class SalesPaymentPartialUpdateSerializer(serializers.ModelSerializer):
    payment_evidence_id32 = serializers.CharField(write_only=True)

    class Meta:
        model = SalesPayment
        fields = ['payment_date', 'payment_evidence_id32', 'status']

    def validate_payment_evidence_id32(self, value):
        try:
            File.objects.get(id32=value)
            return value
        except File.DoesNotExist:
            raise serializers.ValidationError(
                _("File with this id32 does not exist."))

    def update(self, instance, validated_data):
        payment_evidence_id32 = validated_data.pop('payment_evidence_id32', None)
        if payment_evidence_id32:
            instance.payment_evidence = File.objects.get(id32=payment_evidence_id32)
        return super().update(instance, validated_data)
