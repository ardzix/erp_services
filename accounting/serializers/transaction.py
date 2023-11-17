from rest_framework import serializers
from ..models import Transaction, Account


class TransactionMixin:
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["account"] = {
            "id32": instance.account.id32,
            "str": instance.account.__str__(),
        }
        return to_representation


class TransactionSerializer(TransactionMixin, serializers.ModelSerializer):
    account_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=Account.objects.all(),
        source="account",
        required=False,
    )

    class Meta:
        model = Transaction
        fields = [
            "id32",
            "account",
            "account_id32",
            "transaction_date",
            "amount",
            "description",
            "transaction_type",
            "attachements",
        ]
        read_only_fields = ["id32", "account"]


class TransactionListSerializer(TransactionMixin, serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id32",
            "account",
            "transaction_date",
            "amount",
            "description",
            "transaction_type",
        ]
