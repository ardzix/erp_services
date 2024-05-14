import datetime
from inventory.models import StockMovement
from purchasing.models import PurchaseOrder
from django.shortcuts import HttpResponse
from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from libs.pagination import CustomPagination
from libs.excel import create_xlsx_file
from ..serializers.accounts_receivable import AccountsReceivableSerializer


class AccountsReceivableViewSet(GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    movement_ids = PurchaseOrder.objects.filter(
        stock_movement__isnull=False).values_list("stock_movement_id", flat=True)
    queryset = StockMovement.objects.filter(
        status=StockMovement.DELIVERED, id__in=list(set(movement_ids)))
    serializer_class = AccountsReceivableSerializer

    @action(methods=["GET"], detail=False, url_path="excel")
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        headers = {
            "customer": "Nama Pelanggan",
            "billing_amount": "Total PO",
            "delivery_date": "Tanggal Pengiriman",
            "delivery_date_time": "Waktu",
            "billing_due_date": "Tanggal Penagihan",
            "down_payment": "DP",
            "margin_amount": "Margin",
            "margin_percent": "% Margin",
            "sales": "Sales",
            "total_billing_amount": "Total Tagihan",
        }

        items = []
        for movement in queryset:
            po = PurchaseOrder.objects.filter(stock_movement=movement).last()
            customer = po.supplier.name
            billing_amount = po.subtotal_after_discount

            items.append({
                "customer": customer,
                "billing_amount": billing_amount,
                "delivery_date": movement.movement_date.strftime("%-d-%b"),
                "delivery_date_time": movement.movement_date.strftime("%H:%M"),
                "billing_due_date": po.billing_due_date.strftime("%-d-%b"),
                "margin_amount": po.margin,
                "margin_percent": po.magin_percent,
                "sales": po.created_by.get_full_name(),
                "down_payment": po.down_payment,
                "total_billing_amount": po.total,
            })

        output = create_xlsx_file(headers, items, True)
        output.seek(0)
        filename = (
            f"accounts_receivable_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        )
        http_response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        http_response["Content-Disposition"] = "attachment; filename=%s" % filename
        http_response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return http_response
