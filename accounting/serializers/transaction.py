from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from ..models import Transaction, Account, JournalEntry
from . import JournalEntrySerializer, AccountRepresentationMixin


class TransactionSerializer(AccountRepresentationMixin, serializers.ModelSerializer):
    account_number = serializers.SlugRelatedField(
        slug_field="number",
        queryset=Account.objects.all(),
        source="account",
        required=False,
    )
    allocations = JournalEntrySerializer(many=True, source='journalentry_set', write_only=True)
    allocations_data = serializers.SerializerMethodField()
    origin_type = serializers.ChoiceField(
        choices=['employee', 'supplier', 'customer'], write_only=True, required=False)
    origin_id32 = serializers.CharField(write_only=True, required=False)

    def get_allocations_data(self, obj):
        allocations = obj.journalentry_set.filter(is_allocation=True)
        return JournalEntrySerializer(allocations, many=True).data

    def handle_origin(self, instance, origin_type, origin_id32):
        if origin_type and origin_id32:
            try:
                # Get the model class based on the 'origin_type' string
                model = ContentType.objects.get(model=origin_type).model_class()
                # Retrieve the specific instance of the model
                origin_instance = model.objects.get(id32=origin_id32)
                instance.content_type = ContentType.objects.get_for_model(origin_instance)
                instance.object_id = origin_instance.id
                instance.save()
            except ContentType.DoesNotExist:
                raise serializers.ValidationError({"origin_type": "Invalid origin type provided"})
            except model.DoesNotExist:
                raise serializers.ValidationError({"origin_id32": f"No {origin_type} found with provided id32"})

    def create(self, validated_data):
        allocations_data = validated_data.pop('journalentry_set', [])
        origin_type = validated_data.pop('origin_type', None)
        origin_id32 = validated_data.pop('origin_id32', None)

        transaction = Transaction.objects.create(**validated_data)

        # Handle the 'origin' using ContentType
        self.handle_origin(transaction, origin_type, origin_id32)

        # Handle the creation of related JournalEntry instances
        for allocation_data in allocations_data:
            JournalEntry.objects.create(transaction=transaction, **allocation_data)

        return transaction
    
    def update(self, instance, validated_data):
        allocations_data = validated_data.pop('journalentry_set', [])
        origin_type = validated_data.pop('origin_type', None)
        origin_id32 = validated_data.pop('origin_id32', None)

        # Update Transaction instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle the 'origin' using ContentType
        self.handle_origin(instance, origin_type, origin_id32)

        # Delete existing JournalEntry instances
        instance.journalentry_set.all().delete()

        # Create new JournalEntry instances
        for allocation_data in allocations_data:
            JournalEntry.objects.create(transaction=instance, **allocation_data)

        return instance


    class Meta:
        model = Transaction
        fields = [
            "id32",
            "transaction_type",
            "account",
            "account_number",
            "transaction_date",
            "amount",
            "description",
            "allocations",
            "allocations_data",
            "attachements",
            "origin_type",
            "origin_id32",
            "origin"
        ]
        read_only_fields = ["id32", "account", "origin"]



class TransactionListSerializer(AccountRepresentationMixin, serializers.ModelSerializer):
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
