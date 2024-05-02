import datetime
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as django_filters
from django.db.models import Sum, F
from django.shortcuts import HttpResponse
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.excel import create_xlsx_file
from common.serializers import FileSerializer
from common.models import File
from ..scripts import generate_invoice_pdf_for_instances
from ..serializers.sales import (SalesOrderSerializer, SalesOrderListSerializer,
                                 SalesOrderDetailSerializer, InvoiceSerializer, SalesPaymentSerializer, SalesPaymentPartialUpdateSerializer)
from ..models import SalesOrder, Invoice, SalesPayment, CustomerVisit, OrderItem


class SalesFilter(CreatedAtFilterMixin):
    status = django_filters.MultipleChoiceFilter(choices=SalesOrder.STATUS_CHOICES, help_text=_(
        'To filter multiple status, use this request example: ?status=requested&status=delivered'))
    id32s = django_filters.CharFilter(method='filter_by_id32s')
    is_paid = django_filters.BooleanFilter(help_text=_(
        '`true` for paid order, `false` for unpaid order'))
    trip_id32s = django_filters.CharFilter(method='filter_by_trip_id32s')

    class Meta:
        model = SalesOrder
        fields = ['created_at_range', 'status', 'id32s']

    def filter_by_id32s(self, queryset, name, value):
        # Split the comma-separated string to get the list of values
        values_list = value.split(',')
        return queryset.filter(id32__in=values_list).order_by('created_at')

    def filter_by_trip_id32s(self, queryset, name, value):
        # Split the comma-separated string to get the list of values
        values_list = value.split(',')
        visits = CustomerVisit.objects.filter(
            trip__id32__in=values_list, sales_order__isnull=False)
        return queryset.filter(id__in=visits.values_list('sales_order', flat=True)).order_by('created_at')


class SalesOrderViewSet(viewsets.ModelViewSet):
    lookup_field = 'id32'
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = SalesFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return SalesOrderListSerializer
        if self.action == 'retrieve':
            return SalesOrderDetailSerializer
        return SalesOrderSerializer

    @action(detail=True, methods=['GET'])
    def invoice(self, request, id32=None):
        try:
            sales_order = self.get_object()
            invoice = sales_order.invoice
            # Assuming you have an InvoiceSerializer for your Invoice model
            serializer = InvoiceSerializer(invoice)
            return Response(serializer.data)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found for this Sales Order."}, status=404)

    @action(detail=False, methods=['GET'])
    def invoices_pdf(self, request, id32=None):
        queryset = self.filter_queryset(self.get_queryset())
        invoices = Invoice.objects.filter(order__in=queryset)
        invoice_id32s = ''.join(invoices.values_list('id32', flat=True))
        filename = f"Invoices_{invoice_id32s}.pdf"
        file = File.objects.filter(description=filename).first()
        if not file:
            file = generate_invoice_pdf_for_instances(queryset)
        return Response(FileSerializer(instance=file).data)

    @action(methods=["GET"], detail=False, url_path="excel")
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        headers = {
            "order_date": "Order Date",
            "invoice_number": "No. Nota",
            "total_amount": "Jumlah",
            "qty": "Quantity",
            "total_margin_amount": "Margin",
            "bonus": "Bonus",
            "customer": "Customer",
            "margin_percent": "% Margin",
        }

        def get_item(so):
            current_order_items = so.order_items.filter(order=so)
            aggragators = current_order_items.aggregate(total_amount=Sum(F('price') * F('quantity')), total_qty=Sum('quantity'),
                                                        total_margin=F('total_amount') - Sum(F('product__base_price') * F('quantity')))
            total_amount = aggragators.get("total_amount") or 0
            total_qty = aggragators.get("total_qty") or 0
            total_margin = aggragators.get("total_margin") or 0

            try:
                margin_percent = round(total_margin/total_amount * 100, 2)
            except:
                margin_percent = 0

            return total_amount, total_qty, total_margin, margin_percent

        items = []
        for so in queryset:
            total_amount, total_qty, total_margin, margin_percent = get_item(
                so)
            invoice_number = so.invoice.id32 if hasattr(
                so, "invoice") else None
            items.append({
                "order_date": so.order_date,
                "invoice_number": invoice_number,
                "total_amount": total_amount,
                "qty": total_qty,
                "total_margin_amount": total_margin,
                "bonus": so.bonus,
                "customer": so.customer.name,
                "margin_percent": margin_percent
            })

        output = create_xlsx_file(headers, items, True)
        output.seek(0)
        filename = (
            f"salesorder_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        )
        http_response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        http_response["Content-Disposition"] = "attachment; filename=%s" % filename
        http_response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return http_response


class SalesPaymentViewSet(viewsets.ModelViewSet):
    queryset = SalesPayment.objects.all().order_by('-created_at')
    serializer_class = SalesPaymentSerializer
    lookup_field = 'id32'
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination
    # To restrict certain actions:
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return SalesPaymentPartialUpdateSerializer
        return super().get_serializer_class()
