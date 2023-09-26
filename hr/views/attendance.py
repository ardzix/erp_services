from rest_framework import viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from libs.pagination import CustomPagination
from ..models import Attendance, Employee
from ..serializers.attendance import ClockInSerializer, ClockOutSerializer, AttendanceDetailSerializer, AttendanceListSerializer

class AttendanceViewSet(mixins.CreateModelMixin, 
                        mixins.RetrieveModelMixin, 
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    
    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    pagination_class = CustomPagination
    lookup_field = 'id32'

    def get_serializer_class(self):
        if self.action == 'clock_in':
            return ClockInSerializer
        elif self.action == 'clock_out':
            return ClockOutSerializer
        elif self.action == 'retrieve':
            return AttendanceDetailSerializer
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
        employee = Employee.objects.get(user=request.user)  # Assuming there's a one-to-one relationship between User and Employee
        attendance = get_object_or_404(Attendance, employee=employee, clock_out__isnull=True)
        
        serializer = ClockOutSerializer(instance=attendance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_by=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#0d8f1001b083153bcee525c4a8088211505d8f03