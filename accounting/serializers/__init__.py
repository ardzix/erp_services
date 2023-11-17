from rest_framework import serializers
from ..models import Account, Tax, GeneralLedger, JournalEntry


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id32", "parent", "name", "description"]
        read_ony_fields = ["id32"]


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ["id32", "name", "rate"]
        read_ony_fields = ["id32"]


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ["id32", "transaction", "journal", "amount", "debit_credit"]
        read_ony_fields = ["id32"]


class GeneralLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralLedger
        fields = ["id32", "account", "balance"]
        read_ony_fields = ["id32"]
