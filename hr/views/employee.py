import datetime
from rest_framework import viewsets, permissions, filters, decorators, response
from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from django.shortcuts import HttpResponse
from libs.pagination import CustomPagination
from libs.excel import create_xlsx_file
from ..models import Department, Employee, LocationTracker, Salary
from ..serializers.employee import (
    DepartmentSerializer,
    EmployeeSerializer,
    LocationTrackerSerializer,
    SalarySerializer,
    SalaryReportSerializer,
)


class SalaryFilter(django_filters.FilterSet):
    pay_date_range = django_filters.CharFilter(
        method="filter_pay_date_range",
        help_text=_(
            "Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]"
        ),
    )

    def filter_pay_date_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(",")
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(pay_date__gte=start_date, pay_date__lte=end_date)
        return queryset


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
    filterset_class = SalaryFilter
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        django_filters.DjangoFilterBackend,
    )
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

        headers = {
            "name": "Nama",
            "bank_account_number": "No. Rekening",
            "incentive": "Insentif",
            "operational_cost": "Uang Ops",
            "bonus": "Bonus",
            "salary": "Gaji Pokok",
            "total": "Jumlah",
        }

        items = []
        for salary in queryset:
            items.append(
                {
                    "name": salary.employee.user.get_full_name(),
                    "bank_account_number": salary.employee.bank_account_number,
                    "incentive": salary.incentive,
                    "operational_cost": salary.operational_cost,
                    "bonus": salary.bonus,
                    "salary": salary.salary,
                    "total": salary.total
                }
            )

        output = create_xlsx_file(headers, items, True)
        output.seek(0)
        filename = (
            f"salary_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        )
        http_response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        http_response["Content-Disposition"] = "attachment; filename=%s" % filename
        http_response["Access-Control-Expose-Headers"] = "Content-Disposition"

        return http_response
