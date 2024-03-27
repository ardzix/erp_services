from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as django_filters
from rest_framework import viewsets, mixins, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from ..models import Category, Account, Tax, Transaction, JournalEntry, GeneralLedger
from ..serializers import AccountSerializer, CategorySerializer,  TaxSerializer, JournalEntrySerializer, GeneralLedgerSerializer
from ..serializers.transaction import TransactionListSerializer, TransactionSerializer




class CategoryFilter(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='exact')
    parent_number = django_filters.CharFilter(field_name='parent__number', lookup_expr='exact')

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
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend, filters.OrderingFilter,)



class AccountFilter(django_filters.FilterSet):
    category_number = django_filters.NumberFilter(field_name='category__number', lookup_expr='exact')
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
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend, filters.OrderingFilter,)


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)

    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer


class JournalEntryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)


class GeneralLedgerViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = GeneralLedger.objects.all()
    serializer_class = GeneralLedgerSerializer
    lookup_field = 'id32'
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)
