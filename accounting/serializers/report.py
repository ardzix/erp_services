from rest_framework import serializers
from ..models import FinancialReport, FinancialStatement, FinancialReportEntry, FinancialEntry


class FinancialReportEntrySerializer(serializers.ModelSerializer):
    order = serializers.SlugRelatedField(
        slug_field='order',
        queryset=FinancialEntry.objects.all(),
        source='entry'
    )
    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["category"] = {
            "number": instance.category.number,
            "str": instance.category.__str__(),
        }
        return to_representation

    class Meta:
        model = FinancialReportEntry
        fields = ["category", "amount", "order"]


class FinancialReportSerializer(serializers.ModelSerializer):
    financial_statement_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=FinancialStatement.objects.all(),
        source='financial_statement',
        required=True,
        write_only=True
    )
    entries = FinancialReportEntrySerializer(many=True, source='financialreportentry_set')

    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["financial_statement"] = {
            "id32": instance.financial_statement.id32,
            "str": instance.financial_statement.__str__(),
        }
        return to_representation

    class Meta:
        model = FinancialReport
        fields = ["id32", "financial_statement",
                  "financial_statement_id32", "start_date", "end_date", "entries"]
        read_only_fields = ["id32", "financial_statement", "entries"]


class FinancialReportListSerializer(FinancialReportSerializer):
    class Meta:
        model = FinancialReport
        fields = ["id32", "financial_statement",
                  "start_date", "end_date"]
        read_only_fields = ["id32", "financial_statement"]
