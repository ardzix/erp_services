from rest_framework import viewsets, permissions, filters, decorators, response
from libs.pagination import CustomPagination
from ..models import Department, Employee, LocationTracker, Salary
from ..serializers.employee import (
    DepartmentSerializer,
    EmployeeSerializer,
    LocationTrackerSerializer,
    SalarySerializer,
    SalaryReportSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ["name"]
    lookup_field = "id32"


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("user", "department").all()
    serializer_class = EmployeeSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
    lookup_field = "id32"
    http_method_names = ["get", "patch", "head", "options", "put"]


class LocationTrackerViewSet(viewsets.ModelViewSet):
    queryset = LocationTracker.objects.all()
    serializer_class = LocationTrackerSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = [
        "employee__user__username",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
    ]
    lookup_field = "id32"
    http_method_names = ["get", "post", "head", "options"]


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = [
        "employee__user__username",
        "employee__user__email",
        "employee__user__first_name",
        "employee__user__last_name",
    ]
    lookup_field = "id32"
    http_method_names = ["get", "post", "head", "options", "patch", "delete"]

    def get_serializer_class(self):
        return {"get_report": SalaryReportSerializer}.get(self.action, SalarySerializer)

    @decorators.action(methods=["GET"], detail=False, url_path="report")
    def get_report(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.action(methods=["GET"], detail=False, url_path="report/excel")
    def get_report_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset)

        return serializer.data
