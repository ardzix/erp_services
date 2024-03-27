from rest_framework import serializers
from ..models import Category, Account, Tax, GeneralLedger, JournalEntry


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id32", "number", "name", "description"]
        read_only_fields = ["id32"]

class AccountSerializer(serializers.ModelSerializer):
    category_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=Category.objects.all(),
        source="category",
        required=True,)
    class Meta:
        model = Account
        fields = ["id32", "category", "category_id32", "number", "name", "description"]
        read_only_fields = ["id32", "category"]


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ["id32", "name", "rate"]
        read_only_fields = ["id32"]


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ["id32", "transaction", "journal", "amount", "debit_credit"]
        read_only_fields = ["id32"]


class GeneralLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralLedger
        fields = ["id32", "account", "balance"]
        read_only_fields = ["id32"]
