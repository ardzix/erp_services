from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from ..models import Attendance, Employee


class BaseAttendanceSerializer(serializers.ModelSerializer):
    def get_location_coordinate(self, obj, location_field):
        location = getattr(obj, location_field, None)
        if location:
            return {
                'latitude': location.y,
                'longitude': location.x
            }
        return None

    def validate_location(self, value):
        try:
            longitude, latitude = value.split(',')
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return Point(float(longitude), float(latitude))


class ClockInSerializer(BaseAttendanceSerializer):
    clock_in_location = serializers.CharField(write_only=True)
    clock_in_location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['clock_in', 'clock_in_location',
                  'clock_in_location_coordinate']

    def get_clock_in_location_coordinate(self, obj):
        return self.get_location_coordinate(obj, location_field='clock_in_location')

    def validate_clock_in_location(self, value):
        return self.validate_location(value)

    def create(self, validated_data):
        request = self.context.get('request')
        employee = Employee.objects.filter(user=request.user).last()
        if not employee:
            raise serializers.ValidationError(
                _("Employee object not found for the given user."))
        attendance = Attendance.objects.create(
            employee=employee, **validated_data)
        return attendance


class ClockOutSerializer(BaseAttendanceSerializer):
    clock_out_location = serializers.CharField(write_only=True)
    clock_out_location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['clock_out', 'clock_out_location',
                  'clock_out_location_coordinate']

    def get_clock_out_location_coordinate(self, obj):
        return self.get_location_coordinate(obj, location_field='clock_out_location')

    def validate_clock_out_location(self, value):
        return self.validate_location(value)


class AttendanceListSerializer(BaseAttendanceSerializer):
    employee = serializers.StringRelatedField()

    class Meta:
        model = Attendance
        fields = ['id32', 'employee', 'clock_in', 'clock_out']


class AttendanceDetailSerializer(BaseAttendanceSerializer):
    employee = serializers.StringRelatedField()
    employee_id32 = serializers.StringRelatedField(source='id32')
    clock_in_location_coordinate = serializers.SerializerMethodField()
    clock_out_location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id32', 'employee', 'employee_id32', 'clock_in', 'clock_in_location', 'clock_in_location_coordinate',
                  'clock_out', 'clock_out_location', 'clock_out_location_coordinate', 'able_checkout']

    def get_clock_in_location_coordinate(self, obj):
        return self.get_location_coordinate(obj, location_field='clock_in_location')

    def get_clock_out_location_coordinate(self, obj):
        return self.get_location_coordinate(obj, location_field='clock_out_location')

class AttendanceUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Attendance
        fields = ['able_checkout']

class EmployeeAttendanceReportSerializer(serializers.ModelSerializer):
    working_days = serializers.IntegerField()
    working_hours = serializers.SerializerMethodField()
    employee_id32 = serializers.StringRelatedField(
        source='id32', read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ('employee_id32', 'employee_name',
                  'working_days', 'working_hours')

    def get_working_hours(self, obj):
        # Assuming working_hours is a timedelta, we convert it to hours
        return round(obj.working_hours.total_seconds() / 3600, 2) if obj.working_hours else 0

    def get_employee_name(self, obj):
        return f"{obj.user.username} ({obj.user.first_name} {obj.user.last_name})"
