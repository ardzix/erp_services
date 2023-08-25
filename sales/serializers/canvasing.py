from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from inventory.models import Product
from ..models import (
    CanvasingTripTemplate,
    CanvasingCustomer,
    CanvasingCustomerProduct,
    CanvasingTrip,
    CanvasingCustomerVisit,
    CanvasingReport,
    Customer
)
from .sales import CustomerSerializer


class CanvassingCustomerProductSerializer(serializers.ModelSerializer):
    product_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=Product.objects.all(),
        help_text=_("Select products intended for this customer"),
        source='product'
    )
    product_name = serializers.CharField(
        source='product.name',
        read_only=True,
        help_text=_("Name of the product")
    )
    
    class Meta:
        model = CanvasingCustomerProduct
        fields = ('product_id32', 'product_name', 'quantity')


class CanvassingCustomerSerializer(serializers.ModelSerializer):
    products = CanvassingCustomerProductSerializer(source='canvasingcustomerproduct_set', many=True)
    customer_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=Customer.objects.all(),
        help_text=_("Select customer intended for this canvasing"),
        source='customer'
    )
    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True,
        help_text=_("Name of the customer")
    )
    class Meta:
        model = CanvasingCustomer
        fields = ('customer_id32', 'customer_name', 'order', 'products')
        read_only_fields = ('id32',)


class CanvassingTripTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanvasingTripTemplate
        fields = ['id32', 'name']
        read_only_fields = ['id32']


class CanvassingTripTemplateDetailSerializer(serializers.ModelSerializer):
    customers = CanvassingCustomerSerializer(
        many=True, source='canvasingcustomer_set')

    class Meta:
        model = CanvasingTripTemplate
        fields = ['id32', 'name', 'customers']
        read_only_fields = ['id32']
    
    def create(self, validated_data):
        canvasing_customers_data = validated_data.pop('canvasingcustomer_set', [])
        
        # Add created_by to the main instance
        trip_template = CanvasingTripTemplate.objects.create(**validated_data)

        for canvasing_customer_data in canvasing_customers_data:
            # Using the correct key here
            products_data = canvasing_customer_data.pop('canvasingcustomerproduct_set', [])
            
            # Create the CanvasingCustomer instance with created_by
            canvasing_customer = CanvasingCustomer.objects.create(template=trip_template, created_by=self.context['request'].user, **canvasing_customer_data)
            
            # Create the CanvasingCustomerProduct instances with created_by
            for product_data in products_data:
                CanvasingCustomerProduct.objects.create(canvasing_customer=canvasing_customer, created_by=self.context['request'].user, **product_data)

        return trip_template

    def update(self, instance, validated_data):
        canvasing_customers_data = validated_data.pop('canvasingcustomer_set', [])

        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Track all IDs for CanvassingCustomer objects to find out which ones to delete
        current_customer_ids = set(instance.canvasingcustomer_set.values_list('id', flat=True))
        provided_customer_ids = {d.get('id') for d in canvasing_customers_data if 'id' in d}

        # Remove CanvassingCustomer objects that are not present in the provided data
        for customer_id in current_customer_ids - provided_customer_ids:
            CanvasingCustomer.objects.get(id=customer_id).delete()

        # Create or update nested items
        for canvasing_customer_data in canvasing_customers_data:
            product_data = canvasing_customer_data.pop('canvasingcustomerproduct_set', [])

            # If an ID is provided, try to update the item
            if 'id' in canvasing_customer_data:
                canvasing_customer = CanvasingCustomer.objects.get(id=canvasing_customer_data.pop('id'))
                for attr, value in canvasing_customer_data.items():
                    setattr(canvasing_customer, attr, value)
                canvasing_customer.save()
            # Otherwise, create a new item
            else:
                canvasing_customer = CanvasingCustomer.objects.create(template=instance, created_by=self.context['request'].user, **canvasing_customer_data)

            current_product_ids = set(canvasing_customer.canvasingcustomerproduct_set.values_list('id', flat=True))
            provided_product_ids = {d.get('id') for d in product_data if 'id' in d}

            # Remove CanvassingCustomerProduct objects not in the provided data
            for product_id in current_product_ids - provided_product_ids:
                CanvasingCustomerProduct.objects.get(id=product_id).delete()

            # Create or update CanvassingCustomerProduct items
            for pd in product_data:
                if 'id' in pd:
                    product_instance = CanvasingCustomerProduct.objects.get(id=pd.pop('id'))
                    for attr, value in pd.items():
                        setattr(product_instance, attr, value)
                    product_instance.save()
                else:
                    CanvasingCustomerProduct.objects.create(canvasing_customer=canvasing_customer, created_by=self.context['request'].user, **pd)

        return instance

class CanvassingTripListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanvasingTrip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'driver', 'status']
        read_only_fields = ['id32']


class CanvassingCustomerVisitSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    class Meta:
        model = CanvasingCustomerVisit
        fields = ['id32', 'customer', 'sales_order', 'status', 'order']
        read_only_fields = ['id32']


class CanvassingTripDetailSerializer(serializers.ModelSerializer):
    template = CanvassingTripTemplateListSerializer()
    customer_visits = CanvassingCustomerVisitSerializer(
        many=True, source='canvasingcustomervisit_set')
    class Meta:
        model = CanvasingTrip
        fields = ['id32', 'template', 'date',
                  'salesperson', 'driver', 'status', 'customer_visits']
        read_only_fields = ['id32']


class CanvassingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanvasingReport
        fields = ['id32', 'trip', 'customer_visit',
                  'customer', 'status', 'sold_products']
        read_only_fields = ['id32']

class GenerateTripsSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    salesperson_username = serializers.CharField(write_only=True)
    driver_username = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(_("End date must be after start date."))
        return data

    def validate_salesperson_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Salesperson with this username does not exist."))
        return user

    def validate_driver_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Driver with this username does not exist."))
        return user


class CanvassingCustomerVisitStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanvasingCustomerVisit
        fields = ['status']
