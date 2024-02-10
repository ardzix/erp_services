from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework import viewsets, filters
from libs.pagination import CustomPagination
from libs.filter import CreatedAtFilterMixin
from ..models import Vehicle, Driver, Job, Drop, STATUS_CHOICES
from ..serializers import VehicleSerializer, DriverSerializer
from ..serializers.job import JobDetailSerializer, JobListSerializer, DropDetailSerializer, DropUpdateSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name', 'license_plate']
    lookup_field = 'id32'

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['name', 'phone_number']
    lookup_field = 'id32'



class JobFilter(CreatedAtFilterMixin):
    date_range = django_filters.CharFilter(
        method='filter_date_range', help_text=_('Put date range in this format: "start_date,end_date" [YYYY-MM-DD,YYYY-MM-DD]'))
    vehicle_id32 = django_filters.CharFilter(field_name="vehicle__id32")
    trip_id32 = django_filters.CharFilter(field_name="trip__id32")
    assigned_driver_id32 = django_filters.CharFilter(field_name="assigned_driver__id32")
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = Job
        fields = ['created_at_range', 'date_range', 'vehicle_id32', 'trip_id32', 'assigned_driver_id32', 'status']

    def filter_date_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(movement_date__gte=start_date, movement_date__lte=end_date)
        return queryset

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobDetailSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    filterset_class = JobFilter
    filter_backends = (django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['vehicle__name', 'assigned_driver__name', 'trip__template__name']
    lookup_field = 'id32'

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        elif self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return JobDetailSerializer
        return super().get_serializer_class()

class DropViewSet(viewsets.GenericViewSet,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.UpdateModelMixin):
    queryset = Drop.objects.all()
    lookup_field = 'id32'
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = CustomPagination 
    serializer_class = DropDetailSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DropDetailSerializer
        elif self.action == 'partial_update':
            return DropUpdateSerializer
        return super().get_serializer_class()
