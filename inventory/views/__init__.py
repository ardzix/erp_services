from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from common.serializers import SetFileSerializer
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


#e920477217b35578fa1e71f7aa5b280771987b13