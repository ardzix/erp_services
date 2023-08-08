from rest_framework import viewsets, permissions
from libs.pagination import CustomPagination
from ..models import Product
from ..serializers.product import ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer, ProductEditSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed

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

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

#e920477217b35578fa1e71f7aa5b280771987b13