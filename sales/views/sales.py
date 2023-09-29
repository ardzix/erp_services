from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from libs.pagination import CustomPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from ..serializers.sales import SalesOrderSerializer, SalesOrderListSerializer, SalesOrderDetailSerializer
from ..models import SalesOrder

class SalesOrderViewSet(viewsets.ModelViewSet):
    lookup_field = 'id32'
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination  # Add your custom pagination class if needed

    def get_serializer_class(self):
        if self.action == 'list':
            return SalesOrderListSerializer
        if self.action == 'retrieve':
            return SalesOrderDetailSerializer
        return SalesOrderSerializer


    


# e920477217b35578fa1e71f7aa5b280771987b13