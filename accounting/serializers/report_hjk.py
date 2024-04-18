from rest_framework import serializers
from django.db import models
from django.contrib.contenttypes.models import ContentType
from common.serializers import FileLiteSerializer
from sales.models import OrderItem
from inventory.models import Unit, StockMovementItem, Warehouse
from ..models import AccountCategory, FinancialReport, FinancialStatement, FinancialReportEntry, FinancialEntry, JournalEntry


class FinancialStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialStatement
        fields = ["id32", "name", "description"]


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

    attachment = FileLiteSerializer(many=False, read_only=True)

    def to_representation(self, instance):
        to_representation = super().to_representation(instance)
        to_representation["financial_statement"] = {
            "id32": instance.financial_statement.id32,
            "str": instance.financial_statement.__str__(),
        }

        if 'grouped_entries' in to_representation:
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
                        "is_amount_string": False,
                        "entries": []
                    }

                # Append the entry to the correct category group
                grouped_entries[parent_cat_number]['entries'].append(entry)
            order_item = OrderItem.objects.filter(order__order_date__gte=instance.start_date, order__order_date__lte=instance.end_date)
            quantities = []
            for quantity in order_item.values('unit').annotate(quantity=models.Sum('quantity')):
                unit = Unit.objects.get(id=quantity.get("unit")).symbol
                quantities.append(f'{quantity.get("quantity")} {unit}')
            grouped_entries['quantity'] = {
                "parent_category_number": '-1',
                "parent_category_name": "Quantity",
                "total_amount": ", ".join(quantities),
                "is_amount_string": True,
                "entries": []
            }

            smi = StockMovementItem.objects.filter(
                stock_movement__movement_date__gte=instance.start_date, 
                stock_movement__movement_date__lte=instance.end_date,
                stock_movement__destination_type=ContentType.objects.get_for_model(Warehouse)
            )
            revenue = grouped_entries[4]['total_amount'] if 4 in grouped_entries and 'total_amount' in grouped_entries[4] else 0
            operational_cost = grouped_entries[6]['total_amount'] if 6 in grouped_entries and 'total_amount' in grouped_entries[6] else 0
            buy_price = smi.aggregate(total_amount=models.Sum('buy_price')).get('total_amount') if smi else 0
            gross_margin = revenue - buy_price
            gross_margin_percent = round(100* gross_margin/revenue, 2) if revenue > 0 else "-"
            net_margin = gross_margin - operational_cost
            net_margin_percent = round(100* net_margin/revenue, 2) if revenue > 0 else "-"

            grouped_entries['gross_margin'] = {
                "parent_category_number": '-1',
                "parent_category_name": "Laba Kotor",
                "total_amount": gross_margin,
                "is_amount_string": False,
                "entries": []
            }

            grouped_entries['gross_margin_percent'] = {
                "parent_category_number": '-1',
                "parent_category_name": "% Laba Kotor",
                "total_amount": f'{gross_margin_percent} %',
                "is_amount_string": True,
                "entries": []
            }

            grouped_entries['operational_cost'] = grouped_entries.pop(6)

            grouped_entries['net_margin'] = {
                "parent_category_number": '-1',
                "parent_category_name": "Laba Bersih",
                "total_amount": net_margin,
                "is_amount_string": False,
                "entries": []
            }

            grouped_entries['net_margin_percent'] = {
                "parent_category_number": '-1',
                "parent_category_name": "% Laba Bersih",
                "total_amount": f'{net_margin_percent} %',
                "is_amount_string": True,
                "entries": []
            }

            # Replace the original list of entries with the grouped entries
            to_representation['grouped_entries'] = list(grouped_entries.values())
        return to_representation

    class Meta:
        model = FinancialReport
        fields = ["id32", "financial_statement", "financial_statement_id32",
                  "start_date", "end_date", "grouped_entries", "attachment"]
        read_only_fields = ["id32", "financial_statement", "grouped_entries"]


class FinancialReportListSerializer(FinancialReportSerializer):
    class Meta:
        model = FinancialReport
        fields = ["id32", "financial_statement", "financial_statement_id32",
                  "start_date", "end_date"]
        read_only_fields = ["id32", "financial_statement"]
