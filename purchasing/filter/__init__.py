from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as django_filters
from rest_framework import filters
from ..models import Supplier, Payable, PurchaseOrder
from libs.filter import CreatedAtFilterMixin


class SupplierFilter(CreatedAtFilterMixin):
    class Meta:
        model = Supplier
        fields = ['created_at_range', 'has_payable']


class PurchaseOrderFilter(CreatedAtFilterMixin, django_filters.FilterSet):
    APPROVAL_CHOICES = [
        ('all', 'All'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    approval = django_filters.ChoiceFilter(
        method='filter_approval', choices=APPROVAL_CHOICES, label='Approval Status'
    )
    supplier_id32 = django_filters.CharFilter(field_name="supplier__id32")

    class Meta:
        model = PurchaseOrder
        # Only model-specific fields go here
        fields = ['approval', 'created_at_range']

    def filter_approval(self, queryset, name, value):
        if value == 'requested':
            return queryset.filter(approved_at__isnull=True, unapproved_at__isnull=True)
        elif value == 'approved':
            return queryset.filter(approved_at__isnull=False, unapproved_at__isnull=True)
        elif value == 'rejected':
            return queryset.filter(approved_at__isnull=True, unapproved_at__isnull=False)
        return queryset  # return all for 'all' and if the choice is not one of the listed above


class PayableFilter(django_filters.FilterSet):
    is_paid = django_filters.BooleanFilter(
        method='filter_is_paid', help_text=_('`true` for paid, `false` for unpaid'))
    supplier_id32 = django_filters.BooleanFilter(
        field_name='supplier__id32', help_text=_('Filter by supplier id32'))
    order_id32 = django_filters.BooleanFilter(
        field_name='order__id32', help_text=_('Filter by order id32'))
    invoice_id23 = django_filters.BooleanFilter(
        field_name='invoice__id32', help_text=_('Filter by invoice id32'))

    def filter_is_paid(self, queryset, name, value):
        if value in [True, False]:
            if value:
                return queryset.filter(paid_at__isnull=False)
            else:
                return queryset.filter(paid_at__isnull=True)
        return queryset

    class Meta:
        model = Payable
        fields = ['is_paid', 'supplier_id32', 'order_id32', 'invoice_id23']
