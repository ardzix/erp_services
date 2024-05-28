from rest_framework import serializers


class AccountsPayableSerializer(serializers.Serializer):
    def to_representation(self, instance):
        supplier = instance.supplier.name
        amount = instance.subtotal_after_discount
        billing_amount = amount - (instance.down_payment or 0)

        return {
            "supplier": supplier,
            "order_date": instance.order_date,
            "amount": amount,
            "down_payment": instance.down_payment,
            "down_payment_date": instance.down_payment_date,
            "billing_amount": billing_amount,
            "billing_due_date": instance.billing_due_date,
        }
