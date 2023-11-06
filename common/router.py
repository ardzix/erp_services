from rest_framework.routers import DefaultRouter
from .views.administrative import (
    AdministrativeLvl1ViewSet, AdministrativeLvl2ViewSet, AdministrativeLvl3ViewSet, AdministrativeLvl4ViewSet)
from .views import FileViewSet, ConfigurationViewSet

router = DefaultRouter()
router.register('file', FileViewSet, basename='file')
router.register('config', ConfigurationViewSet, basename='config')
router.register('administrative_lv1', AdministrativeLvl1ViewSet,
                basename='administrative_lv1')
router.register('administrative_lv2', AdministrativeLvl2ViewSet,
                basename='administrative_lv2')
router.register('administrative_lv3', AdministrativeLvl3ViewSet,
                basename='administrative_lv3')
router.register('administrative_lv4', AdministrativeLvl4ViewSet,
                basename='administrative_lv4')
