from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as django_filters
from django.db.models import Q
from rest_framework import viewsets, mixins, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from ..models import Category, Account, Tax, Transaction, JournalEntry, GeneralLedger
from ..serializers import AccountSerializer, CategorySerializer,  TaxSerializer, JournalEntrySerializer, GeneralLedgerSerializer
from ..serializers.transaction import TransactionListSerializer, TransactionSerializer


class CategoryFilter(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='exact')
    parent_number = django_filters.CharFilter(
        field_name='parent__number', lookup_expr='exact')

    class Meta:
        model = Category
        fields = ['number', 'parent_number']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'number'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = CategoryFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)
    search_fields = ['number', 'name']


class AccountFilter(django_filters.FilterSet):
    category_number = django_filters.NumberFilter(
        field_name='category__number', lookup_expr='exact')
    number = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Account
        fields = ['category_number', 'number']


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    lookup_field = 'number'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = AccountFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)
    search_fields = ['number', 'name']


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)


class TransactionFilter(django_filters.FilterSet):
    account_category_number = django_filters.NumberFilter(method='filter_account_category_number',
                                                          help_text='Put exact account category number to filter')
    account_number = django_filters.CharFilter(field_name='account__number', lookup_expr='iexact',
                                               help_text='Put exact account number to filter')
    transaction_type = django_filters.ChoiceFilter(choices=Transaction.TRANSACTION_TYPES,
                                                   help_text='Filter by type: cash_in or cash_out')
    transaction_date_range = django_filters.CharFilter(method='filter_transaction_date_range',
                                                       help_text=_('Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))

    def filter_account_category_number(self, queryset, name, value):
        if value:
            return queryset.filter(Q(account__category__number=value) | Q(account__category__parent__number=value))

    def filter_transaction_date_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(transaction_date__gte=start_date, transaction_date__lte=end_date)
        return queryset

    class Meta:
        model = Transaction
        fields = ['account_category_number', 'account_number',
                  'transaction_type', 'transaction_date_range']


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = TransactionFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)

    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer


class JournalEntryFilter(django_filters.FilterSet):
    account_category_number = django_filters.NumberFilter(method='filter_account_category_number',
                                                          help_text='Put exact account category number to filter')
    account_number = django_filters.CharFilter(field_name='account__number', lookup_expr='iexact',
                                               help_text='Put exact account number to filter')
    debit_credit = django_filters.ChoiceFilter(choices=JournalEntry.DEBIT_CREDIT_CHOICES,
                                               help_text='Filter by type: debit or credit')
    transaction_date_range = django_filters.CharFilter(method='filter_transaction_date_range',
                                                       help_text=_('Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))

    def filter_account_category_number(self, queryset, name, value):
        if value:
            return queryset.filter(Q(account__category__number=value) | Q(account__category__parent__number=value))

    def filter_transaction_date_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(transaction__transaction_date__gte=start_date, transaction_date__lte=end_date)
        return queryset

    class Meta:
        model = JournalEntry
        fields = ['account_category_number', 'account_number',
                  'debit_credit', 'transaction_date_range']


class JournalEntryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = JournalEntryFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)


class GeneralLedgerViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = GeneralLedger.objects.all()
    serializer_class = GeneralLedgerSerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)
