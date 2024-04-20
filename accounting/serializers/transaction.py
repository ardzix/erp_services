from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from identities.models import Contact
from common.serializers import FileLiteSerializer
from ..models import Transaction, Account, JournalEntry, TransactionCategory
from . import JournalEntrySerializer, AccountRepresentationMixin


class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = ["code", "name", "prefix", "description"]


class TransactionSerializer(AccountRepresentationMixin, serializers.ModelSerializer):
    account_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=Account.objects.all(),
        source="account",
        required=False,
    )
    transaction_type = serializers.SlugRelatedField(
        slug_field="code",
        queryset=TransactionCategory.objects.all(),
        required=True,
    )
    allocations = JournalEntrySerializer(
        many=True, source='journalentry_set', write_only=True)
    allocations_data = serializers.SerializerMethodField()
    source_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Contact.objects.all(),
        source='source',
        required=True,
        write_only=True
    )
    allocation_str = serializers.SerializerMethodField()
    attachment = FileLiteSerializer(many=False, read_only=True)

    def get_allocation_queryset(self, obj):
        return obj.journalentry_set.filter(is_allocation=True)

    def get_allocations_data(self, obj):
        return JournalEntrySerializer(self.get_allocation_queryset(obj), many=True).data
    
    def get_allocation_str(self, obj):
        allocations = self.get_allocation_queryset(obj)
        allocation_str = []
        for allocation in allocations:
            allocation_str.append(f'{allocation.account.number} - {allocation.account.name}')
        return ", ".join(allocation_str)



    def create(self, validated_data):
        allocations_data = validated_data.pop('journalentry_set', [])

        transaction = Transaction.objects.create(**validated_data)

        # Handle the creation of related JournalEntry instances
        for allocation_data in allocations_data:
            JournalEntry.objects.create(
                transaction=transaction, **allocation_data)

        return transaction

    def update(self, instance, validated_data):
        allocations_data = validated_data.pop('journalentry_set', [])

        # Update Transaction instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


        # Delete existing JournalEntry instances
        instance.journalentry_set.all().delete()

        # Create new JournalEntry instances
        for allocation_data in allocations_data:
            JournalEntry.objects.create(
                transaction=instance, **allocation_data)

        return instance

    class Meta:
        model = Transaction
        fields = [
            'id32',
            'number',
            'account',
            'account_number',
            'allocations',
            'allocation_str',
            'allocations_data',
            'amount',
            'attachements',
            'description',
            'source',
            'source_id32',
            'transaction_date',
            'transaction_type',
            'attachment'
        ]
        read_only_fields = ["id32", "account", "source"]


class TransactionListSerializer(TransactionSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id32",
            "account",
            "allocation_str",
            "transaction_date",
            "amount",
            "description",
            "transaction_type",
        ]
