from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, mixins, filters
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from ..models import StockMovement, StockMovementItem
from ..serializers.stock_movement import (StockMovementListSerializer, StockMovementDetailSerializer, StockMovementItemListSerializer,
                                          StockMovementCreateSerializer, StockMovementItemSerializer, StockMovementItemUpdateSerializer)


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
    status = django_filters.ChoiceFilter(choices=StockMovement.MOVEMENT_STATUS)

    class Meta:
        model = StockMovement
        fields = ['created_at_range', 'movement_date_range', 'origin_type', 'destination_type',
                  'origin_filter', 'destination_filter', 'status']

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
                return queryset.filter(movement_date__gte=start_date, movement_date__lte=end_date)
        return queryset


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = StockMovementFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return StockMovementListSerializer
        elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return StockMovementCreateSerializer
        return StockMovementDetailSerializer


class StockMovementItemStatusUpdateViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = StockMovementItem.objects.all()
    lookup_field = 'id32'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StockMovementItemSerializer
        return StockMovementItemUpdateSerializer