from rest_framework import viewsets, permissions
from libs.pagination import CustomPagination
from rest_framework import viewsets, mixins
from ..models import Supplier
from ..serializers.supplier import (
    SupplierListSerializer, 
    SupplierDetailSerializer, 
    SupplierCreateSerializer, 
    SupplierEditSerializer
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

