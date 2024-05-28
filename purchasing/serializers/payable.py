from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from ..models import Payable


class PayableSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['supplier'] = {
            'id32': instance.supplier.id32,
            'str': instance.supplier.__str__(),
        }
        representation['order'] = {
            'id32': instance.order.id32,
            'str': instance.order.__str__(),
        }
        representation['stock_movement'] = {
            'id32': instance.stock_movement.id32,
            'str': instance.stock_movement.__str__(),
        }
        if instance.shipment:
            representation['shipment'] = {
                'id32': instance.shipment.id32,
                'str': instance.shipment.__str__(),
            }
        if instance.payment:
            representation['payment'] = {
                'id32': instance.payment.id32,
                'str': instance.payment.__str__(),
            }
        return representation

    class Meta:
        model = Payable
        fields = ['id32', 'supplier', 'order', 'stock_movement', 'shipment', 'payment', 'amount', 'paid_at',
                  'less_30_days_amount', 'less_60_days_amount', 'less_90_days_amount', 'more_than_90_days_amount'
                  ]
        read_only_fields = ['id32', 'supplier', 'order',
                            'stock_movement', 'payment']
