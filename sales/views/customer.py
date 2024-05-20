import datetime
from django.contrib.gis.db.models import Avg
from django.db import connection
from django.db.models import F, Sum
from django.shortcuts import HttpResponse
from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, filters
from libs.pagination import CustomPagination
from libs.filter import CreatedAtFilterMixin
from libs.excel import create_xlsx_file
from ..serializers.customer import CustomerSerializer, CustomerListSerializer, CustomerMapSerializer, StoreTypeSerializer, CustomerCreateSerializer
from ..models import Customer, StoreType, OrderItem


class CustomerFilter(CreatedAtFilterMixin):
    id32s = django_filters.CharFilter(method='filter_by_id32s')
    order_created_at_range = django_filters.CharFilter(method='filter_order_created_at_range', help_text=_(
        'Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))
    created_by_id = django_filters.CharFilter(
        method='filter_created_by_id', help_text=_("Filter by created_by_id"))

    def filter_order_created_at_range(self, queryset, name, value):
        return queryset

    def filter_created_by_id(self, queryset, name, value):
        return queryset


class StoreTypeViewSet(viewsets.ModelViewSet):
    lookup_field = 'id32'
    queryset = StoreType.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination
    serializer_class = StoreTypeSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer API endpoints.

    retrieve:
    Return a customer instance based on the given id32.

    list:
    Return a list of all existing customers.

    create:
    Create a new customer instance. Ensure that all required fields are provided.

    delete:
    Remove an existing customer.

    update:
    Update fields in an existing customer. Ensure that all required fields are provided.

    partial_update:
    Update certain fields in an existing customer without affecting others.

    """
    lookup_field = 'id32'
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = CustomerFilter

    def get_serializer_class(self):
        return {
            "list": CustomerListSerializer,
            "map": CustomerMapSerializer,
            "create": CustomerCreateSerializer,
            "excel": None
        }.get(self.action, CustomerSerializer)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        order_created_at_range = request.query_params.get(
            "order_created_at_range")
        created_by_id = request.query_params.get("created_by_id")
        order_items = OrderItem.objects.filter(order__customer__in=queryset)
        if order_created_at_range:
            order_created_at_range = order_created_at_range.split(',')
            if len(order_created_at_range) == 2:
                start_date, end_date = order_created_at_range
                order_items = order_items.filter(
                    order__created_at__gte=start_date, order__created_at__lte=end_date)
        if created_by_id and created_by_id.isdigit():
            order_items = order_items.filter(
                order__created_by_id=int(created_by_id))
            customer_ids = order_items.values_list(
                "order__customer_id", flat=True)
            queryset = queryset.filter(id__in=list(set(customer_ids)))

        context = {"order_items": order_items}

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, context=context)
            return Response(serializer.data)

    def create(self, requests, *args, **kwargs):
        return super().create(requests, *args, **kwargs)

    def update(self, requests, *args, **kwargs):
        return super().update(requests, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def map(self, request):
        # Define the SQL to fetch average latitude and longitude
        raw_sql = """
        SELECT 
            AVG(ST_Y(location::geometry)) as avg_latitude, 
            AVG(ST_X(location::geometry)) as avg_longitude 
        FROM sales_customer
        """

        # Execute the raw SQL
        with connection.cursor() as cursor:
            cursor.execute(raw_sql)
            avg_coords = cursor.fetchone()

        # Fetching serialized data
        queryset = self.get_queryset()
        serializer = CustomerMapSerializer(queryset, many=True)

        return Response({
            "center": {
                "latitude": avg_coords[0],
                "longitude": avg_coords[1]
            },
            "markers": serializer.data
        })

    @action(methods=["GET"], detail=False, url_path="excel")
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        order_created_at_range = request.query_params.get(
            "order_created_at_range")
        order_items = OrderItem.objects.filter(order__customer__in=queryset)
        if order_created_at_range:
            order_created_at_range = order_created_at_range.split(',')
            if len(order_created_at_range) == 2:
                start_date, end_date = order_created_at_range
                order_items = order_items.filter(
                    order__created_at__gte=start_date, order__created_at__lte=end_date)

        headers = {
            "customer": "Customer",
            "omzet": "Omzet",
            "qty": "Quantity",
            "margin": "Margin",
            "margin_percent": "% Margin"
        }

        def get_item(customer):
            current_order_items = order_items.filter(order__customer=customer)
            aggragators = current_order_items.aggregate(total_omzet=Sum(F('price') * F('quantity')), total_qty=Sum('quantity'),
                                                        total_margin=F('total_omzet') - Sum(F('product__base_price') * F('quantity')))
            total_omzet = aggragators.get("total_omzet") or 0
            total_qty = aggragators.get("total_qty") or 0
            total_margin = aggragators.get("total_margin") or 0

            try:
                margin_percent = round(total_margin/total_omzet * 100, 2)
            except:
                margin_percent = 0

            return total_omzet, total_qty, total_margin, margin_percent

        items = []
        for customer in queryset:
            total_omzet, total_qty, total_margin, margin_percent = get_item(
                customer)
            items.append({
                "customer": customer.name,
                "omzet": total_omzet,
                "qty": total_qty,
                "margin": total_margin,
                "margin_percent": margin_percent
            })

        output = create_xlsx_file(headers, items, True)
        output.seek(0)
        filename = (
            f"customer_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        )
        http_response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        http_response["Content-Disposition"] = "attachment; filename=%s" % filename
        http_response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return http_response
