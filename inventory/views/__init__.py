from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from common.serializers import SetFileSerializer
from ..models import Product, StockMovement, Unit, Category, StockMovementItem, Warehouse
from ..serializers.product import ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer, ProductEditSerializer
from ..serializers.stock_movement import StockMovementListSerializer, StockMovementDetailSerializer, StockMovementCreateSerializer, StockMovementItemSerializer
from ..serializers.unit import UnitCreateUpdateSerializer, UnitDetailSerializer, UnitListSerializer
from ..serializers.category import CategoryListSerializer, CategoryDetailSerializer
from ..serializers.warehouse import WarehouseSerializer, WarehouseListSerializer


def get_model_from_name(model_name):
    return ContentType.objects.get(model=model_name.lower())


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductEditSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], serializer_class=SetFileSerializer)
    def set_picture(self, request, id32=None):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_instance = serializer.save()

        # Link it to the product
        product.picture = file_instance
        product.save()

        return Response({"message": "Picture set successfully!"}, status=status.HTTP_200_OK)


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
        'Put destionation in this format: "origin_type,origin_id32". Example: "warehouse,A"'))
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
    serializer_class = StockMovementDetailSerializer
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = StockMovementFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return StockMovementListSerializer
        elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return StockMovementCreateSerializer
        return super().get_serializer_class()


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UnitListSerializer
        elif self.action == 'retrieve':
            return UnitDetailSerializer
        return UnitCreateUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategoryDetailSerializer


class StockMovementItemViewSet(viewsets.ModelViewSet):
    queryset = StockMovementItem.objects.all()
    serializer_class = StockMovementItemSerializer
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['stock_movement__id32']
    ordering_fields = ['id']

    def get_queryset(self):
        # Custom filtering to allow filtering by stock_movement id32
        queryset = super().get_queryset()
        stock_movement_id32 = self.request.query_params.get('stock_movement')
        if stock_movement_id32:
            queryset = queryset.filter(
                stock_movement__id32=stock_movement_id32)
        return queryset


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter, django_filters.DjangoFilterBackend]
    search_fields = ['name', 'address']
    filterset_fields = ['type']

    def get_serializer_class(self):
        if self.action == 'list':
            return WarehouseListSerializer
        return WarehouseSerializer
