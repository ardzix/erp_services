from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, CompanyProfileViewSet, BrandViewSet
from .views.user_group import UserViewSet, GroupViewSet

router = DefaultRouter()
router.register('user_profile', UserProfileViewSet, basename='user_profile')
router.register('company_profile', CompanyProfileViewSet, basename='company_profile')
router.register('brand', BrandViewSet, basename='brand')
router.register('user', UserViewSet, basename='user')
router.register('group', GroupViewSet, basename='group')
