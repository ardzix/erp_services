from rest_framework import serializers
from django.db.models import F, Sum
from django.contrib.gis.geos import Point
from ..models import SalesOrder, OrderItem, Customer

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        
class SalesOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()

    def get_total_amount(self, obj):
        total_amount = obj.order_items.aggregate(total_price=Sum(F('price') * F('quantity'))).get('total_price')
        return f'{total_amount:,.0f}'

    class Meta:
        model = SalesOrder
        fields = ['id32', 'customer', 'order_date', 'approved_by', 'total_amount', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        sales_order = SalesOrder.objects.create(**validated_data)

        for item_data in order_items_data:
            OrderItem.objects.create(order=sales_order, **item_data)

        return sales_order


class CustomerSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()

    def get_location_coordinate(self, obj):
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None

    class Meta:
        model = Customer
        fields = ['id32', 'name', 'contact_number', 'address', 'location', 'location_coordinate', 'company_profile']

    def create(self, validated_data):
        # Convert the coordinates to a Point object
        location_data = validated_data.pop('location')
        longitude, latitude = location_data.split(',')
        validated_data['location'] = Point(float(longitude), float(latitude))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Convert the coordinates to a Point object
        location_data = validated_data.pop('location')
        longitude, latitude = location_data.split(',')
        validated_data['location'] = Point(float(longitude), float(latitude))
        return super().update(instance, validated_data)
    
class CustomerLiteSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = ['id32', 'name', 'contact_number', 'address', 'location_coordinate']
