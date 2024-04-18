from rest_framework import serializers
from django.db import models
from ..models import AccountCategory, FinancialReport, FinancialStatement, FinancialReportEntry, FinancialEntry, JournalEntry


class FinancialReportEntrySerializer(serializers.ModelSerializer):
    parent_category = serializers.SlugRelatedField(
        slug_field='parent',
        queryset=AccountCategory.objects.all(),
        source='category'
    )
    order = serializers.SlugRelatedField(
        slug_field='order',
        queryset=FinancialEntry.objects.all(),
        source='entry'
    )

    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["parent_category"] = {
            "number": instance.category.parent.number,
            "name": instance.category.parent.name,
        }
        to_representation["category"] = {
            "number": instance.category.number,
            "name": instance.category.name,
        }
        return to_representation

    class Meta:
        model = FinancialReportEntry
        fields = ["parent_category", "category", "amount", "order"]


class FinancialReportSerializer(serializers.ModelSerializer):
    financial_statement_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=FinancialStatement.objects.all(),
        source='financial_statement',
        required=True,
        write_only=True
    )
    grouped_entries = FinancialReportEntrySerializer(
        many=True, source='financialreportentry_set')

    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["financial_statement"] = {
            "id32": instance.financial_statement.id32,
            "str": instance.financial_statement.__str__(),
        }

        # Initialize a dictionary to hold the grouped entries
        grouped_entries = {}

        # Loop through each entry in the serialized data
        for entry in to_representation['grouped_entries']:
            parent_category = entry.pop('parent_category')
            parent_cat_number = parent_category['number']
            parent_cat_name = parent_category['name']

            # Create a key for each unique parent category
            if parent_cat_number not in grouped_entries:

                journals = JournalEntry.objects.filter(
                    account__category__parent__number=parent_cat_number, 
                    transaction__transaction_date__gte=instance.start_date, 
                    transaction__transaction_date__lte=instance.end_date)
                total_amount = journals.aggregate(
                    total_amount=models.Sum('amount')).get('total_amount')
                grouped_entries[parent_cat_number] = {
                    "parent_category_number": parent_cat_number,
                    "parent_category_name": parent_cat_name,
                    "total_amount": total_amount,
                    "entries": []
                }

            # Append the entry to the correct category group
            grouped_entries[parent_cat_number]['entries'].append(entry)

        # Replace the original list of entries with the grouped entries
        to_representation['grouped_entries'] = list(grouped_entries.values())
        return to_representation

    class Meta:
        model = FinancialReport
        fields = ["id32", "financial_statement",
                  "financial_statement_id32", "start_date", "end_date", "grouped_entries"]
        read_only_fields = ["id32", "financial_statement", "grouped_entries"]


class FinancialReportListSerializer(FinancialReportSerializer):
    class Meta:
        model = FinancialReport
        fields = ["id32", "financial_statement",
                  "start_date", "end_date"]
        read_only_fields = ["id32", "financial_statement"]
