from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as django_filters
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, filters
from libs.pagination import CustomPagination
from ..models import AccountCategory, Account, Tax, TransactionCategory, Transaction, JournalEntry, GeneralLedger, ModuleAccount
from ..serializers import AccountSerializer, AccountCategorySerializer, TaxSerializer, JournalEntrySerializer, GeneralLedgerSerializer, ModuleAccountSerializer, ModuleAccountTransactionChoiceSerializer
from ..serializers.transaction import TransactionListSerializer, TransactionSerializer, TransactionCategorySerializer
from ..helpers.constant import DEBIT_CREDIT_CHOICES, TRANSACTION_CHOICES, TRANSACTION_MODULE_CHOICES


class AccountCategoryFilter(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='exact')
    parent_number = django_filters.CharFilter(
        field_name='parent__number', lookup_expr='exact')

    class Meta:
        model = AccountCategory
        fields = ['number', 'parent_number']


class AccountCategoryViewSet(viewsets.ModelViewSet):
    queryset = AccountCategory.objects.all()
    serializer_class = AccountCategorySerializer
    lookup_field = 'number'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = AccountCategoryFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)
    search_fields = ['number', 'name']


class AccountFilter(django_filters.FilterSet):
    category_number = django_filters.NumberFilter(
        field_name='category__number', lookup_expr='exact')
    category_number = django_filters.NumberFilter(method='filter_category_number',
                                                  help_text='Put exact account category number to filter')
    number = django_filters.CharFilter(lookup_expr='contains')

    def filter_category_number(self, queryset, name, value):
        if value:
            return queryset.filter(Q(category__number=value) | Q(category__parent__number=value))

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


class TransactionCategoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionCategory.objects.all()
    serializer_class = TransactionCategorySerializer
    lookup_field = 'code'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)
    search_fields = ['code', 'name']


class TransactionFilter(django_filters.FilterSet):
    account_category_number = django_filters.NumberFilter(method='filter_account_category_number',
                                                          help_text='Put exact account category number to filter')
    account_number = django_filters.CharFilter(field_name='account__number', lookup_expr='iexact',
                                               help_text='Put exact account number to filter')
    transaction_type = django_filters.CharFilter(field_name='transaction_type__code', lookup_expr='iexact',
                                                 help_text='Put exact transaction type code to filter')
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
                  'transaction_date_range']


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
    debit_credit = django_filters.ChoiceFilter(choices=DEBIT_CREDIT_CHOICES,
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


class ModuleAccountFilter(django_filters.FilterSet):
    account_category_number = django_filters.NumberFilter(method='filter_account_category_number',
                                                          help_text='Put exact account category number to filter')
    account_number = django_filters.CharFilter(field_name='account__number', lookup_expr='iexact',
                                               help_text='Put exact account number to filter')
    debit_credit = django_filters.ChoiceFilter(choices=DEBIT_CREDIT_CHOICES,
                                               help_text='Filter by type: debit or credit')
    transaction = django_filters.ChoiceFilter(choices=TRANSACTION_CHOICES,
                                              help_text='Filter by type: debit or credit')

    def filter_account_category_number(self, queryset, name, value):
        if value:
            return queryset.filter(Q(account__category__number=value) | Q(account__category__parent__number=value))

    class Meta:
        model = ModuleAccount
        fields = ['transaction', 'account_category_number',
                  'account_number', 'debit_credit']


class ModuleAccountViewSet(viewsets.ModelViewSet):
    queryset = ModuleAccount.objects.all()
    serializer_class = ModuleAccountSerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = ModuleAccountFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend, filters.OrderingFilter,)


class ModuleAccountTransactionChoiceView(APIView):

    def get(self, request, *args, **kwargs):
        # Convert choices tuple to a format suitable for serialization
        choices_list = [{'code': choice[0], 'name': choice[1]} for choice in TRANSACTION_MODULE_CHOICES]
        serializer = ModuleAccountTransactionChoiceSerializer(choices_list, many=True)
        return Response(serializer.data)