from django_filters import rest_framework as django_filters
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.filter import CreatedAtFilterMixin
from libs.pagination import CustomPagination
from libs.permission import CanApprovePurchaseOrderPermission
from inventory.models import Product
from ..models import Supplier, SupplierProduct, PurchaseOrder, InvalidPOItem
from ..serializers.supplier import (
    SupplierListSerializer,
    SupplierDetailSerializer,
    SupplierCreateSerializer,
    SupplierEditSerializer,
    SupplierProductSerializer,
    BulkAddProductsSerializer
)
from ..serializers.purchase_order import (
    PurchaseOrderListSerializer, PurchaseOrderDetailSerializer, InvalidPOItemSerializer, PODownPaymentSerializer)
from ..filter import SupplierFilter



class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = SupplierFilter
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['name', 'contact_number', 'address']
    lookup_field = 'id32'

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
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['supplier__name', 'product__name']
    lookup_field = 'id32'

    @action(detail=False, methods=['post'], serializer_class=BulkAddProductsSerializer)
    def bulk_add(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        supplier = serializer.validated_data['supplier']
        product_ids = [product.id for product in Product.objects.filter(
            id32__in=serializer.validated_data['products'])]

        # Create SupplierProduct for each product
        for product_id in product_ids:
            SupplierProduct.objects.create(
                supplier=supplier, product_id=product_id, created_by=request.user)

        return Response({"detail": "Products added successfully to the supplier."})


class PurchaseOrderFilter(CreatedAtFilterMixin, django_filters.FilterSet):
    APPROVAL_CHOICES = [
        ('all', 'All'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    approval = django_filters.ChoiceFilter(
        method='filter_approval', choices=APPROVAL_CHOICES, label='Approval Status'
    )

    class Meta:
        model = PurchaseOrder
        # Only model-specific fields go here
        fields = ['approval', 'created_at_range']

    def filter_approval(self, queryset, name, value):
        if value == 'requested':
            return queryset.filter(approved_at__isnull=True, unapproved_at__isnull=True)
        elif value == 'approved':
            return queryset.filter(approved_at__isnull=False, unapproved_at__isnull=True)
        elif value == 'rejected':
            return queryset.filter(approved_at__isnull=True, unapproved_at__isnull=False)
        return queryset  # return all for 'all' and if the choice is not one of the listed above


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().prefetch_related(
        'purchaseorderitem_set')  # Prefetch to reduce the number of queries
    serializer_class = PurchaseOrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = PurchaseOrderFilter
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['supplier__name']
    lookup_field = 'id32'

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        elif self.action == 'down_payment':
            return PODownPaymentSerializer
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

    @action(detail=True, methods=["post"])
    def down_payment(self, request, id32=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.down_payment = serializer.validated_data["down_payment"]
        instance.down_payment_date = serializer.validated_data["down_payment_date"]
        instance.save()

        return Response({"detail": "Update Down Payment of Purchase Order successfully."})


class InvalidPOItemViewSet(viewsets.ModelViewSet):
    queryset = InvalidPOItem.objects.all()
    serializer_class = InvalidPOItemSerializer
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    http_method_names = ['post', 'patch', 'head', 'options']
