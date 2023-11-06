# views.py

from rest_framework import viewsets, permissions
from libs.pagination import CustomPagination
from ..models import Department, Employee
from ..serializers.employee import DepartmentSerializer, EmployeeSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    http_method_names = ['get', 'patch', 'head', 'options', 'put']