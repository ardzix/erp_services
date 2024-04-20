from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, ContactViewSet, BrandViewSet

router = DefaultRouter()
router.register('user_profile', UserProfileViewSet, basename='user_profile')
router.register('company_profile', ContactViewSet, basename='company_profile')
router.register('brand', BrandViewSet, basename='brand')