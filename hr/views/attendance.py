import django_filters
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, F, DurationField, When, Case, Q
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from ..models import Attendance, Employee
from ..serializers.attendance import (ClockInSerializer, ClockOutSerializer,
                                      AttendanceDetailSerializer, AttendanceListSerializer, EmployeeAttendanceReportSerializer)



class AttendanceFilter(django_filters.FilterSet):
    year_month = django_filters.CharFilter(method='filter_year_month', help_text=_('Year and month in YYYY-MM format'))
    employee_search = django_filters.CharFilter(method='filter_employee')

    class Meta:
        model = Attendance
        fields = ['year_month']


    def filter_year_month(self, queryset, name, value):
        # Split the value into year and month
        try:
            year, month = map(int, value.split('-'))
            # Filter based on year and month
            return queryset.filter(
                Q(clock_in__year=year) & Q(clock_in__month=month)
            )
        except ValueError:
            # In case of an invalid format, return an empty queryset or handle as needed
            return queryset.none()

    def filter_employee(self, queryset, name, value):
        return queryset.filter(
            Q(employee__user__username__icontains=value) |
            Q(employee__user__first_name__icontains=value) |
            Q(employee__user__last_name__icontains=value)
        )

class AttendanceViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    filterset_class = AttendanceFilter
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    lookup_field = 'id32'

    def get_serializer_class(self):
        if self.action == 'clock_in':
            return ClockInSerializer
        elif self.action == 'clock_out':
            return ClockOutSerializer
        elif self.action == 'retrieve':
            return AttendanceDetailSerializer
        elif self.action == 'monthly_report':
            return EmployeeAttendanceReportSerializer
        else:  # This covers the 'list' action and any other actions not specified
            return AttendanceListSerializer

    @action(detail=False, methods=['POST'])
    def clock_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(created_by=self.request.user)
        return Response(ClockInSerializer(instance).data)

    @action(detail=False, methods=['POST'])
    def clock_out(self, request):
        # Assuming there's a one-to-one relationship between User and Employee
        employee = Employee.objects.get(user=request.user)
        attendance = get_object_or_404(
            Attendance, employee=employee, clock_out__isnull=True)

        serializer = ClockOutSerializer(instance=attendance, data=request.data, context={
                                        'request': request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_by=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        year_month = self.request.query_params.get('year_month')
        if not year_month:
            return Response({"error": _("Year and month in 'YYYY-MM' format are required.")}, status=status.HTTP_400_BAD_REQUEST)
        
        # Split the year and month
        try:
            year, month = map(int, year_month.split('-'))
        except ValueError:
            return Response({"error": _("Year and month must be in 'YYYY-MM' format.")}, status=status.HTTP_400_BAD_REQUEST)

        # Filter the queryset for the provided month and calculate the working days
        queryset = Employee.objects.annotate(
            working_days=Count('attendance', filter=Q(attendance__clock_in__year=year, attendance__clock_in__month=month)),
            working_hours=Sum(
                Case(
                    When(attendance__clock_out__isnull=False, then=F('attendance__clock_out') - F('attendance__clock_in')),
                    default=None,
                    output_field=DurationField()
                ),
                filter=Q(attendance__clock_in__year=year, attendance__clock_in__month=month)
            )
        )
        
        # Filter based on employee search if it is provided
        employee_search = self.request.query_params.get('employee_search')
        if employee_search:
            queryset = queryset.filter(
                Q(user__username__icontains=employee_search) |
                Q(user__first_name__icontains=employee_search) |
                Q(user__last_name__icontains=employee_search)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmployeeAttendanceReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EmployeeAttendanceReportSerializer(queryset, many=True)
        return Response(serializer.data)