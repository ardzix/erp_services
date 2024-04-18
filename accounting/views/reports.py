from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from rest_framework import viewsets, permissions, filters, mixins
from libs.pagination import CustomPagination
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import TruncDay, TruncMonth, Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from ..models import Transaction, FinancialReport, FinancialStatement
from ..serializers.report import FinancialReportSerializer, FinancialReportListSerializer, FinancialStatementSerializer
from ..filters import TransactionFilter
from ..helpers.constant import SALES_ORDER




class FinancialStatementViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = FinancialStatement.objects.all()
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    serializer_class = FinancialStatementSerializer

class TransactionSaleReportViewSet(viewsets.ViewSet):
    """
    A ViewSet for viewing transaction sales statistics.
    """
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionFilter

    def get_queryset(self):
        """
        Restricts the returned sales to transactions marked as SALE.
        """
        queryset = Transaction.objects.filter(transaction_type=SALES_ORDER)
        return queryset

    @action(detail=False, methods=['get'], url_path='sales-statistics')
    def sales_statistics(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Retrieve 'aggregate_by' from query parameters
        aggregate_by = request.query_params.get('aggregate_by', 'monthly')
        
        # Aggregate data
        if aggregate_by == 'daily':
            aggregated_data = queryset.annotate(date=TruncDay('transaction_date')) \
                                      .values('date') \
                                      .annotate(total_sales=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())) \
                                      .order_by('date')
        else:  # Monthly aggregation
            aggregated_data = queryset.annotate(month=TruncMonth('transaction_date')) \
                                      .values('month') \
                                      .annotate(total_sales=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())) \
                                      .order_by('month')

        # Prepare the result set
        result_set = self.prepare_result_set(aggregated_data, aggregate_by)

        return Response(result_set)

    def prepare_result_set(self, aggregated_data, aggregate_by):
        today = timezone.now()
        if aggregate_by == 'daily':
            start_date = today - timedelta(days=30)
            dates_range = [start_date + timedelta(days=x) for x in range(31)]
        else:  # Monthly aggregation
            start_date = today - timedelta(days=365)
            dates_range = [start_date + timedelta(days=30*x) for x in range(12)]

        result_set = {date.strftime('%Y-%m-%d'): 0 for date in dates_range}
        
        for entry in aggregated_data:
            key = entry['date'].strftime('%Y-%m-%d') if 'date' in entry else entry['month'].strftime('%Y-%m-%d')
            result_set[key] = entry['total_sales']

        formatted_result = [{"month": key, "total_sales": value} for key, value in result_set.items()]
        return formatted_result

    def filter_queryset(self, queryset):
        """
        Apply the configured filters to the queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset



class FinancialReporttFilter(django_filters.FilterSet):
    financial_statement_id32 = django_filters.CharFilter(field_name='financial_statement__id32', lookup_expr='iexact',
                                               help_text='Put financial statement id32 to filter')

    class Meta:
        model = FinancialReport
        fields = ['financial_statement_id32']


class FinancialReportViewSet(viewsets.ModelViewSet):
    queryset = FinancialReport.objects.all()
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = FinancialReporttFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)

    def get_serializer_class(self):
        if self.action == 'list':
            return FinancialReportListSerializer
        return FinancialReportSerializer