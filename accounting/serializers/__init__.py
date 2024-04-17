from rest_framework import serializers
from ..models import AccountCategory, Account, Tax, GeneralLedger, JournalEntry, ModuleAccount
from ..helpers.constant import TRANSACTION_CHOICES, TRANSACTION_MODULE_CHOICES


class AccountRepresentationMixin:

    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        if instance.account:
            to_representation["account"] = {
                "number": instance.account.number,
                "category": instance.account.category.parent.__str__(),
                "sub_category": instance.account.category.__str__(),
                "str": instance.account.__str__(),
            }
        return to_representation


class AccountCategorySerializer(serializers.ModelSerializer):
    parent_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=AccountCategory.objects.all(),
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
        model = AccountCategory
        fields = ["parent_number", "parent", "number", "name", "description"]
        read_only_fields = ["parent"]


class AccountSerializer(serializers.ModelSerializer):
    category_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=AccountCategory.objects.all(),
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
        fields = ["category", "category_number",
                  "number", "name", "description"]
        read_only_fields = ["category"]


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ["id32", "name", "rate"]
        read_only_fields = ["id32"]


class JournalEntrySerializer(AccountRepresentationMixin, serializers.ModelSerializer):
    account_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=Account.objects.all(),
        source="account",
        required=True,
        write_only=True)

    class Meta:
        model = JournalEntry
        fields = ["id32", "account_number", "account",
                  "journal", "amount", "debit_credit"]
        read_only_fields = ["id32", "account"]


class GeneralLedgerSerializer(AccountRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = GeneralLedger
        fields = ["id32", "account", "balance"]
        read_only_fields = ["id32"]



class ModuleAccountSerializer(AccountRepresentationMixin, serializers.ModelSerializer):
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["name"] = {
            "key": instance.name,
            "str": dict(TRANSACTION_MODULE_CHOICES).get(instance.name),
        }
        to_representation["transaction"] = {
            "key": instance.transaction,
            "str": dict(TRANSACTION_CHOICES).get(instance.transaction),
        }
        return to_representation
    class Meta:
        model = ModuleAccount
        fields = ["id32", "name", "transaction", "account", "debit_credit"]
        read_only_fields = ["id32"]
