from rest_framework import serializers
from ..models import PurchaseOrder, StockMovement


class AccountsReceivableSerializer(serializers.Serializer):
    def to_representation(self, instance):
        po = PurchaseOrder.objects.filter(stock_movement=instance).last()
        customer = po.supplier.name
        billing_amount = po.subtotal_after_discount

        return {
            "customer": customer,
            "billing_amount": billing_amount,
            "delivery_date": instance.movement_date.date(),
            "delivery_date_time": instance.movement_date.strftime("%H:%M"),
            "billing_due_date": po.billing_due_date,
            "margin_amount": po.margin,
            "margin_percent": po.magin_percent,
            "sales": po.created_by.get_full_name(),
            "down_payment": po.down_payment,
            "total_billing_amount": po.total,
        }
