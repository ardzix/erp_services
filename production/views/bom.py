from django_filters import rest_framework as django_filters
from rest_framework import viewsets, filters
from libs.pagination import CustomPagination
from libs.filter import CreatedAtFilterMixin
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from ..models import BillOfMaterials, BOMProduct, BOMComponent
from ..serializers.bom import BillOfMaterialsSerializer, BOMProductSerializer, BOMComponentSerializer

    
class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.all()
    serializer_class = BillOfMaterialsSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filterset_class = CreatedAtFilterMixin
    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name']
    lookup_field = 'id32'

    def perform_create(self, serializer):
        serializer.save()
        self._save_relations(serializer)

    def perform_update(self, serializer):
        serializer.save()
        self._save_relations(serializer)

    def _save_relations(self, serializer):
        instance = serializer.instance
        products_data = serializer.validated_data.get('bomproduct_set', [])
        components_data = serializer.validated_data.get('bomcomponent_set', [])
        
        # Handle products
        for product_data in products_data:
            BOMProduct.objects.update_or_create(defaults=product_data, bom=instance, product=product_data['product'])
        
        # Handle components
        for component_data in components_data:
            BOMComponent.objects.update_or_create(defaults=component_data, bom=instance, component=component_data['component'])

        # Here you might want to handle deletions if necessary
