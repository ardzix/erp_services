from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from common.models import File
from ..models import PurchaseOrderPayment, PurchaseOrder


class PurchaseOrderPaymentSerializer(serializers.ModelSerializer):
    purchase_order_id32 = serializers.CharField(write_only=True)
    payment_evidence_id32 = serializers.CharField(
        write_only=True, required=False)

    class Meta:
        model = PurchaseOrderPayment
        fields = [
            'id32', 'purchase_order_id32', 'purchase_order', 'amount', 'payment_date',
            'payment_evidence_id32', 'payment_evidence', 'status'
        ]
        read_only_fields = ['id32', 'purchase_order', 'payment_evidence']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.purchase_order:
            representation['purchase_order'] = {
                'id32': instance.purchase_order.id32,
                'str': instance.purchase_order.__str__(),
            }
        if instance.payment_evidence:
            representation['payment_evidence'] = {
                'id32': instance.payment_evidence.id32,
                'url': instance.payment_evidence.file.url,
            }

        status_dict = dict(PurchaseOrderPayment.STATUS_CHOICES)
        representation['status'] = {
            'key': instance.status,
            'value': status_dict.get(instance.status, ""),
        }
        return representation

    def validate_purchase_order_id32(self, value):
        try:
            PurchaseOrder.objects.get(id32=value)
            return value
        except PurchaseOrder.DoesNotExist:
            raise serializers.ValidationError(
                _("PurchaseOrder with this id32 does not exist."))

    def validate_payment_evidence_id32(self, value):
        try:
            File.objects.get(id32=value)
            return value
        except File.DoesNotExist:
            raise serializers.ValidationError(
                _("File with this id32 does not exist."))

    def create(self, validated_data):
        purchase_order_id32 = validated_data.pop('purchase_order_id32', None)
        if purchase_order_id32:
            validated_data['purchase_order'] = PurchaseOrder.objects.get(
                id32=purchase_order_id32)
        file_id32 = validated_data.pop('payment_evidence_id32', None)
        if file_id32:
            validated_data['payment_evidence'] = File.objects.get(
                id32=file_id32)
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(e)
