from rest_framework import viewsets, permissions, status, filters
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from common.serializers import SetFileSerializer
from ..models import Product, StockMovement, Unit, Category, StockMovementItem, Warehouse
from ..serializers.product import ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer, ProductEditSerializer
from ..serializers.stock_movement import StockMovementListSerializer, StockMovementDetailSerializer, StockMovementCreateSerializer, StockMovementItemSerializer
from ..serializers.unit import UnitCreateUpdateSerializer, UnitDetailSerializer, UnitListSerializer
from ..serializers.category import CategoryListSerializer, CategoryDetailSerializer
from ..serializers.warehouse import WarehouseSerializer, WarehouseListSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
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


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination 
    serializer_class = StockMovementDetailSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return StockMovementListSerializer
        elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return StockMovementCreateSerializer
        return super().get_serializer_class()
    


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
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
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination 

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategoryDetailSerializer


class StockMovementItemViewSet(viewsets.ModelViewSet):
    queryset = StockMovementItem.objects.all()
    serializer_class = StockMovementItemSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
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
            queryset = queryset.filter(stock_movement__id32=stock_movement_id32)
        return queryset



class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination 
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, django_filters.DjangoFilterBackend]
    search_fields = ['name', 'address']
    filterset_fields = ['type']

    def get_serializer_class(self):
        if self.action == 'list':
            return WarehouseListSerializer
        return WarehouseSerializer
