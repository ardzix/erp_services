from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from ..models import TripTemplate, Trip, CustomerVisitReport, CustomerVisit
from ..serializers.canvasing import (
    TripTemplateListSerializer,
    TripTemplateDetailSerializer,
    TripListSerializer,
    TripDetailSerializer,
    CustomerVisitSerializer,
    CanvassingReportSerializer,
    GenerateTripsSerializer,
    CustomerVisitStatusSerializer
)

class TripTemplateViewSet(viewsets.ModelViewSet):
    queryset = TripTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed
    serializer_class = TripTemplateDetailSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'put']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TripTemplateListSerializer
        elif self.action == 'generate_trips':
            return GenerateTripsSerializer
        return TripTemplateDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_trips(self, request, id32=None):    
        trip_template = self.get_object()
        serializer = GenerateTripsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        salesperson = serializer.validated_data['salesperson_username']
        driver = serializer.validated_data['driver_username']
        
        trips = trip_template.generate_trips(start_date, end_date, salesperson, driver)

        return Response(TripListSerializer(trips, many=True).data)

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed
    serializer_class = TripDetailSerializer
    http_method_names = ['get', 'patch', 'delete', 'head', 'options', 'put']

    def get_serializer_class(self):
        if self.action == 'list':
            return TripListSerializer
        return TripDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_report(self, request, pk=None):
        trip = self.get_object()

        # Your method to generate the report
        report_data = trip.generate_report()  # Placeholder, define this method on the CanvassingTrip model

        # Storing report data in CanvassingReport model
        report = CustomerVisitReport.objects.create(trip=trip, **report_data)
        
        return Response(CanvassingReportSerializer(report).data)

class CustomerVisitViewSet(viewsets.ModelViewSet):
    queryset = CustomerVisit.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed
    serializer_class = CustomerVisitSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = CustomerVisitReport.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination  # Add your custom pagination class if needed
    serializer_class = CanvassingReportSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class CustomerVisitStatusUpdateViewSet(viewsets.GenericViewSet):
    queryset = CustomerVisit.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    serializer_class = CustomerVisitStatusSerializer
    lookup_field = 'id32'

    def partial_update(self, request, id32=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)