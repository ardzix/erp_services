from rest_framework.routers import DefaultRouter
from .views.bom import BillOfMaterialsViewSet

router = DefaultRouter()
router.register('bill-of-materials', BillOfMaterialsViewSet, basename='bill-of-materials')
