from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from ..models import Customer, Receivable

class CustomerFilter(filters.FilterSet):

    class Meta:
        model = Customer
        fields = ['payment_type', 'has_receivable']

class ReceivableFilter(filters.FilterSet):
    is_paid = filters.BooleanFilter(method='filter_is_paid',help_text=_('`true` for paid, `false` for unpaid'))
    customer_id32 = filters.BooleanFilter(field_name='customer__id32',help_text=_('Filter by customer id32'))
    order_id32 = filters.BooleanFilter(field_name='order__id32',help_text=_('Filter by order id32'))
    invoice_id23 = filters.BooleanFilter(field_name='invoice__id32',help_text=_('Filter by invoice id32'))

    def filter_is_paid(self, queryset, name, value):
        if value in [True, False]:
            if value:
                return queryset.filter(paid_at__isnull=False)
            else:
                return queryset.filter(paid_at__isnull=True)
        return queryset
        
    class Meta:
        model = Receivable
        fields = ['is_paid', 'customer_id32', 'order_id32', 'invoice_id23']