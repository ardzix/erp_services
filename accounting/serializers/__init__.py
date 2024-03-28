from rest_framework import serializers
from ..models import Category, Account, Tax, GeneralLedger, JournalEntry


class CategorySerializer(serializers.ModelSerializer):
    parent_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=Category.objects.all(),
        source="parent",
        required=False,
        write_only=True)
    
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        if instance.parent:
            to_representation["parent"] = {
                "number": instance.parent.number,
                "str": instance.parent.__str__(),
            }
        return to_representation
    class Meta:
        model = Category
        fields = ["parent_number", "parent", "number", "name", "description"]
        read_only_fields = ["parent"]

class AccountSerializer(serializers.ModelSerializer):
    category_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=Category.objects.all(),
        source="category",
        required=True,
        write_only=True)
    
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["category"] = {
            "number": instance.category.number,
            "str": instance.category.__str__(),
        }
        return to_representation
    class Meta:
        model = Account
        fields = ["category", "category_number", "number", "name", "description"]
        read_only_fields = ["category"]


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ["id32", "name", "rate"]
        read_only_fields = ["id32"]


class JournalEntrySerializer(serializers.ModelSerializer):
    account_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=Account.objects.all(),
        source="account",
        required=True,
        write_only=True)
    
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["account"] = {
            "number": instance.account.number,
            "str": instance.account.__str__(),
        }
        return to_representation
    
    class Meta:
        model = JournalEntry
        fields = ["id32", "account_number", "account", "journal", "amount", "debit_credit", "is_allocation"]
        read_only_fields = ["id32", "account", "debit_credit", "is_allocation"]


class GeneralLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralLedger
        fields = ["id32", "account", "balance"]
        read_only_fields = ["id32"]
