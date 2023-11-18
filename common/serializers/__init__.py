import base64
from datetime import date, timedelta
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import serializers
from libs.utils import get_config_value
from libs.constants import MOBILE_ROLE_MENU_MAP
from slugify import slugify
from ..models import File


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class FileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ('name', 'file', 'url', 'description')

    def get_url(self, instance):
        return instance.file.url if instance.file else '-'


def decode_base64_img(encoded_file, name='temp'):
    file_format, imgstr = encoded_file.split(';base64,')
    ext = file_format.split('/')[-1]

    # Add padding if required
    missing_padding = len(imgstr) % 4
    if missing_padding:
        imgstr += '=' * (4 - missing_padding)

    data = ContentFile(base64.b64decode(imgstr), name=name+'.' + ext)
    return data


class FileCreateSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    file_base64 = serializers.CharField(
        write_only=True, help_text="Base64 encoded file data")

    class Meta:
        model = File
        fields = ('id32', 'name', 'url', 'file_base64', 'description')
        read_only_fields = ['id32']

    def get_url(self, instance):
        return instance.file.url if instance.file else '-'

    def validate(self, data):
        encoded_file = data.pop('file_base64')
        data['file'] = decode_base64_img(encoded_file, name=data['name'])
        return data


class SetFileSerializer(serializers.Serializer):
    file_base64 = serializers.CharField(
        write_only=True, help_text="Base64 encoded file data")

    def create(self, validated_data):
        user = self.context.get('request').user
        encoded_file = validated_data['file_base64']
        data = decode_base64_img(encoded_file)

        # Create File instance
        file_instance = File.objects.create(
            name=data.name, file=data, created_by=user)
        return file_instance


class MeSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)
    check_in = serializers.SerializerMethodField()
    last_attendance = serializers.SerializerMethodField()
    sales_trips = serializers.SerializerMethodField()
    driver_jobs = serializers.SerializerMethodField()
    collector_trips = serializers.SerializerMethodField()
    header_text = serializers.SerializerMethodField()
    has_request_item = serializers.SerializerMethodField()
    can_request_item = serializers.SerializerMethodField()
    trip_template_id32s = serializers.SerializerMethodField()
    warehouse_assignment_id32s = serializers.SerializerMethodField()
    menus = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'groups', 'check_in', 'last_attendance',
                  'sales_trips', 'driver_jobs',
                  'collector_trips', 'header_text', 'has_request_item',
                  'trip_template_id32s', 'warehouse_assignment_id32s', 'menus']

    def get_check_in(self, instance):
        from hr.models import Attendance

        attendance = Attendance.objects.filter(
            employee__user=instance, clock_out__isnull=True).last()
        return {
            'is_checked_in': True if attendance else False,
            'clock_in': attendance.clock_in if attendance else None,
            'attendance_id32': attendance.id32 if attendance else None,
            'able_checkout': attendance.able_checkout if attendance else None
        }

    def get_last_attendance(self, instance):
        from hr.models import Attendance

        attendance = Attendance.objects.filter(
            employee__user=instance, clock_out__isnull=False).last()
        return {
            'clock_in': attendance.clock_in if attendance else None,
            'clock_out': attendance.clock_out if attendance else None,
            'attendance_id32': attendance.id32 if attendance else None,
        }
    
    def trip_qs(self, instance):
        from sales.models import Trip
        return Trip.objects.filter(salesperson=instance, date=date.today())

    def get_sales_trips(self, instance):
        from sales.serializers.trip import TripListSerializer

        trips = self.trip_qs(instance)
        return TripListSerializer(trips, many=True).data

    def get_driver_jobs(self, instance):
        from logistics.models import Job
        from logistics.serializers.job import JobListSerializer

        jobs = Job.objects.filter(
            assigned_driver__owned_by=instance, date=date.today())
        return JobListSerializer(jobs, many=True).data

    def get_collector_trips(self, instance):
        from sales.models import Trip
        from sales.serializers.trip import TripListSerializer

        trips = Trip.objects.filter(salesperson=instance, date=date.today())
        return TripListSerializer(trips, many=True).data

    def get_header_text(self, instance):
        first_line = get_config_value('header_text_1st_line', 'Artriz ERP')
        second_line = get_config_value(
            'header_text_2nd_line', 'You can configure this text from the dashboard')
        return f'{first_line}\n{second_line}'

    def get_has_request_item(self, instance):
        from inventory.models import StockMovement
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return StockMovement.objects.filter(created_by=instance, movement_date__gte=tomorrow).exists()

    def get_trip_template_id32s(self, instance):
        from sales.models import TripTemplate
        return TripTemplate.objects.filter(pic=instance).values_list('id32', flat=True)

    def get_warehouse_assignment_id32s(self, instance):
        from inventory.models import Warehouse
        return Warehouse.objects.filter(pic=instance).values_list('id32', flat=True)
    
    def get_menus(self, instance):
        from django.contrib.auth.models import Group
        roles = instance.groups.values_list('name', flat=True)
        slugified_roles = [slugify(x) for x in roles]
        mobile_menus = []
        for role in slugified_roles:
            if role in dict(MOBILE_ROLE_MENU_MAP):
                mobile_menus += dict(MOBILE_ROLE_MENU_MAP).get(role)
        return {
            'mobile': list(set(mobile_menus)),
            'dashboard': []
        }