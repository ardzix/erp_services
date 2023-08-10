from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from rest_framework import viewsets, mixins
from inventory.models import Product
from ..models import Supplier, SupplierProduct
from ..serializers.supplier import (
    SupplierListSerializer, 
    SupplierDetailSerializer, 
    SupplierCreateSerializer, 
    SupplierEditSerializer,
    SupplierProductSerializer,
    BulkAddProductsSerializer
)

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed

    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierListSerializer
        elif self.action == 'retrieve':
            return SupplierDetailSerializer
        elif self.action == 'create':
            return SupplierCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SupplierEditSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SupplierProductViewSet(viewsets.ModelViewSet):
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], serializer_class=BulkAddProductsSerializer)
    def bulk_add(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        supplier = serializer.validated_data['supplier']
        product_ids = [product.id for product in Product.objects.filter(id32__in=serializer.validated_data['products'])]

        # Create SupplierProduct for each product
        for product_id in product_ids:
            SupplierProduct.objects.create(supplier=supplier, product_id=product_id, created_by=request.user)

        return Response({"detail": "Products added successfully to the supplier."})

#e920477217b35578fa1e71f7aa5b280771987b13