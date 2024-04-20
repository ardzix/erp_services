from rest_framework import viewsets, permissions
from libs.pagination import CustomPagination
from ..models import UserProfile, Contact, Brand
from ..serializers import (
    UserProfileSerializer, 
    UserProfileDetailSerializer,
    ContactSerializer,
    BrandSerializer,
    FileSerializer
)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination 

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserProfileDetailSerializer
        return UserProfileSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination 

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination 
