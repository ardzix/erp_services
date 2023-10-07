from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.decorators import action
from libs.pagination import CustomPagination
from ..serializers.sales import (SalesOrderSerializer, SalesOrderListSerializer, 
SalesOrderDetailSerializer, InvoiceSerializer, SalesPaymentSerializer, SalesPaymentPartialUpdateSerializer)
from ..models import SalesOrder, Invoice, SalesPayment


class SalesOrderViewSet(viewsets.ModelViewSet):
    lookup_field = 'id32'
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination

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
