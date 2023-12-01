from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum
from rest_framework import viewsets, permissions, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from ..models import StockMovement, StockMovementItem
from ..serializers.stock_movement import (StockMovementListSerializer, 
                                          StockMovementDetailSerializer, 
                                          StockMovementItemPOBatchSerializer,
                                          StockMovementCreateSerializer, 
                                          StockMovementItemSerializer, 
                                          StockMovementItemUpdateSerializer,
                                          DistinctStockMovementItemSerializer,
                                          StockMovementItemBulkUpdateSerializer)


def get_model_from_name(model_name):
    return ContentType.objects.get(model=model_name.lower())


class StockMovementFilter(CreatedAtFilterMixin):
    ORIGIN_DESTINATION_TYPE_CHOICES = (
        ('warehouse', 'Warehouse'),
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
    )
    movement_date_range = django_filters.CharFilter(
        method='filter_movement_date_range', help_text=_('Put date range in this format: "start_date,end_date" [YYYY-MM-DD,YYYY-MM-DD]'))
    origin_type = django_filters.ChoiceFilter(field_name='origin_type__model',
                                              choices=ORIGIN_DESTINATION_TYPE_CHOICES,
                                              help_text='Filter by origin type. Options: warehouse, supplier, customer.')
    destination_type = django_filters.ChoiceFilter(field_name='destination_type__model',
                                                   choices=ORIGIN_DESTINATION_TYPE_CHOICES,
                                                   help_text='Filter by destination type. Options: warehouse, supplier, customer.')
    origin_filter = django_filters.CharFilter(method='filter_origin', help_text=_(
        'Put origin in this format: "origin_type,origin_id32". Example: "warehouse,A"'))
    destination_filter = django_filters.CharFilter(method='filter_destination', help_text=_(
        'Put destionation in this format: "destination_type,destination_id32". Example: "warehouse,A"'))
    status = django_filters.MultipleChoiceFilter(choices=StockMovement.MOVEMENT_STATUS, help_text=_(
        'To filter multiple status, use this request example: ?status=requested&status=delivered'))
    id32s = django_filters.CharFilter(method='filter_by_id32s')

    class Meta:
        model = StockMovement
        fields = ['created_at_range', 'movement_date_range', 'origin_type', 'destination_type',
                  'origin_filter', 'destination_filter', 'status', 'id32s']

    def filter_origin(self, queryset, name, value):
        if value:
            origin = value.split(',')
            try:
                model, id32 = origin
                content_type = get_model_from_name(model)
                Model = content_type.model_class()
                obj = Model.objects.get(id32=id32)
                return queryset.filter(origin_type=content_type, origin_id=obj.id)
            except:
                return queryset.filter(id=0)
        return queryset

    def filter_destination(self, queryset, name, value):
        if value:
            destination = value.split(',')
            try:
                model, id32 = destination
                content_type = get_model_from_name(model)
                Model = content_type.model_class()
                obj = Model.objects.get(id32=id32)
                return queryset.filter(destination_type=content_type, destination_id=obj.id)
            except:
                return queryset.filter(id=0)
        return queryset

    def filter_movement_date_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(
                    Q(movement_date__gte=start_date, movement_date__lte=end_date) | Q(
                        movement_date__isnull=True)
                )
        return queryset

    def filter_by_id32s(self, queryset, name, value):
        # Split the comma-separated string to get the list of values
        values_list = value.split(',')
        return queryset.filter(id32__in=values_list).order_by('created_at')


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = StockMovementFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return StockMovementListSerializer
        elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return StockMovementCreateSerializer
        elif self.action == 'new_item_batch':
            return StockMovementItemPOBatchSerializer
        return StockMovementDetailSerializer

    @action(detail=True, methods=['post'])
    def new_item_batch(self, request, id32=None):
        """
        Add new stock movement item batch.
        """
        stock_movement = self.get_object()
        serializer = StockMovementItemPOBatchSerializer(
            data=request.data,
            # Pass the stock_movement to serializer's context
            context={'stock_movement': stock_movement}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def distinct_items(self, request, id32=None):
        stock_movement = self.get_object()
        distinct_items = StockMovementItem.objects.filter(stock_movement=stock_movement)\
                                                  .values('product__id32', 'product__name', 'unit__id32', 'unit__name', 'stock_movement')\
                                                  .annotate(total_quantity=Sum('quantity'))\
                                                  .order_by('product__name', 'unit__name')
        serializer = DistinctStockMovementItemSerializer(distinct_items, many=True)
        return Response(serializer.data)


class StockMovementItemViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = StockMovementItem.objects.all()
    lookup_field = 'id32'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StockMovementItemSerializer
        elif self.action == 'bulk_update':
            return StockMovementItemBulkUpdateSerializer
        return StockMovementItemUpdateSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id32': openapi.Schema(type=openapi.TYPE_STRING),
                    'origin_movement_status': openapi.Schema(type=openapi.TYPE_STRING),
                    'destination_movement_status': openapi.Schema(type=openapi.TYPE_STRING),
                    'expire_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        )
    )
    @action(detail=False, methods=['patch'], url_path='bulk-update')
    def bulk_update(self, request):
        # Retrieve the instances first
        id32s = [item.get('id32') for item in request.data]
        instances = StockMovementItem.objects.filter(id32__in=id32s)

        serializer = StockMovementItemBulkUpdateSerializer(instances, data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'bulk update successful'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)