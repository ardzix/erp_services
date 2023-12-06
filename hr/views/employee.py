from rest_framework import viewsets, permissions, filters
from libs.pagination import CustomPagination
from ..models import Department, Employee, LocationTracker
from ..serializers.employee import DepartmentSerializer, EmployeeSerializer, LocationTrackerSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['name']
    lookup_field = 'id32'

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    lookup_field = 'id32'
    http_method_names = ['get', 'patch', 'head', 'options', 'put']


class LocationTrackerViewSet(viewsets.ModelViewSet):
    queryset = LocationTracker.objects.all()
    serializer_class = LocationTrackerSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ['employee__user__username', 'employee__user__email', 'employee__user__first_name', 'employee__user__last_name']
    lookup_field = 'id32'
    http_method_names = ['get', 'post', 'head', 'options']