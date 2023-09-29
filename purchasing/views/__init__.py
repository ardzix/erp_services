from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from libs.pagination import CustomPagination
from libs.permission import CanApprovePurchaseOrderPermission
from rest_framework import viewsets, mixins
from inventory.models import Product
from ..models import Supplier, SupplierProduct, PurchaseOrder
from ..serializers.supplier import (
    SupplierListSerializer, 
    SupplierDetailSerializer, 
    SupplierCreateSerializer, 
    SupplierEditSerializer,
    SupplierProductSerializer,
    BulkAddProductsSerializer
)
from ..serializers.purchase_order import PurchaseOrderListSerializer, PurchaseOrderDetailSerializer

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


    



class SupplierProductViewSet(viewsets.ModelViewSet):
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed



    


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


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().prefetch_related('purchaseorderitem_set')  # Prefetch to reduce the number of queries
    serializer_class = PurchaseOrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderDetailSerializer


    


    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanApprovePurchaseOrderPermission])
    def approve(self, request, id32=None):
        instance = self.get_object()

        # Check if the instance is already approved
        if instance.approved_at:
            return Response({"detail": "Purchase Order is already approved."}, status=status.HTTP_400_BAD_REQUEST)

        instance.approved_by = request.user
        instance.approved_at = timezone.now()
        instance.unapproved_by = None
        instance.unapproved_at = None
        instance.save()

        return Response({"detail": "Purchase Order approved successfully."})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanApprovePurchaseOrderPermission])
    def reject(self, request, id32=None):
        instance = self.get_object()

        # Check if the instance is already rejected
        if instance.unapproved_at:
            return Response({"detail": "Purchase Order is already unapproved."}, status=status.HTTP_400_BAD_REQUEST)

        instance.approved_by = None
        instance.approved_at = None
        instance.unapproved_by = request.user
        instance.unapproved_at = timezone.now()
        instance.save()

        return Response({"detail": "Purchase Order unapproved successfully."})


#e920477217b35578fa1e71f7aa5b280771987b13