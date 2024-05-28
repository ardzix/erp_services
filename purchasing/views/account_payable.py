import datetime
from purchasing.models import PurchaseOrder
from django.shortcuts import HttpResponse
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import filters
from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework.decorators import action
from libs.pagination import CustomPagination
from libs.excel import create_xlsx_file

from ..serializers.accounts_payable import AccountsPayableSerializer

from django_filters import rest_framework as django_filters


class AccountsPayableFilter(django_filters.FilterSet):
    order_date_range = django_filters.CharFilter(
        method='filter_order_date_range', help_text=_('Put date range in this format: "start_date,end_date" [YYYY-MM-DD,YYYY-MM-DD]'))

    def filter_order_date_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(order_date__date__gte=start_date, order_date__date__lte=end_date)
        return queryset


class AccountsPayableViewSet(GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = PurchaseOrder.objects.filter()
    serializer_class = AccountsPayableSerializer
    filterset_class = AccountsPayableFilter
    filter_backends = (filters.SearchFilter,
                       django_filters.DjangoFilterBackend)
    search_fields = ["supplier__name"]

    @action(methods=["GET"], detail=False, url_path="excel")
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        headers = {
            "supplier": "Vendor",
            "order_date": "Tanggal",
            "amount": "Nominal",
            "down_payment_date": "Tanggal DP",
            "down_payment": "Nominal DP",
            "billing_amount": "Jumlah",
            "billing_due_date": "Jatuh Tempo",
        }

        items = []
        for po in queryset:
            supplier = po.supplier.name
            amount = po.subtotal_after_discount
            billing_amount = amount - (po.down_payment or 0)

            items.append({
                "supplier": supplier,
                "order_date": str(po.order_date),
                "amount": amount,
                "down_payment": po.down_payment,
                "down_payment_date": str(po.down_payment_date) if po.down_payment_date else None,
                "billing_amount": billing_amount,
                "billing_due_date": str(po.billing_due_date)
            })

        output = create_xlsx_file(headers, items, True)
        output.seek(0)
        filename = (
            f"accounts_payable_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        )
        http_response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        http_response["Content-Disposition"] = "attachment; filename=%s" % filename
        http_response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return http_response
