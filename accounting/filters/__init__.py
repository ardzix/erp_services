from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from django.db.models import Exists, OuterRef
from django.utils import timezone
from ..models import Transaction, JournalEntry

class TransactionFilter(filters.FilterSet):
    end_date = filters.DateFilter(field_name="transaction_date", lookup_expr='lte', method='default_end_date')
    payment_status = filters.CharFilter(method='filter_payment_status', help_text=_('Choice: `paid` or `unpaid` or `all`'))
    aggregated_by = filters.CharFilter(method='filter_aggregated_by', required=False, help_text=_('Choice: `daily` or `monthly`'))

    def default_end_date(self, queryset, name, value):
        if value is None:
            value = timezone.now()
        return queryset.filter(**{name: value})
    
    def filter_payment_status(self, queryset, name, value):
        payment_entries = JournalEntry.objects.filter(
            transaction_id=OuterRef('pk'),
            journal__icontains="Cash and Cash Equivalents"
        )
        
        if value == 'paid':
            return queryset.annotate(has_payment=Exists(payment_entries)).filter(has_payment=True)
        elif value == 'unpaid':
            return queryset.annotate(has_payment=Exists(payment_entries)).filter(has_payment=False)
        return queryset

    def filter_aggregated_by(self, queryset, name, value):
        today = timezone.now()
        if value == 'monthly':
            start_date = today - timezone.timedelta(days=365)
        elif value == 'daily':
            start_date = today - timezone.timedelta(days=30)
        else:
            return queryset
        
        return queryset.filter(transaction_date__gte=start_date)

    class Meta:
        model = Transaction
        fields = []
