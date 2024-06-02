# serializers.py

from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from libs.utils import handle_location
from ..models import Department, Employee, LocationTracker, Salary


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id32", "name"]
        read_only_fields = ["id32"]


class EmployeeSerializer(serializers.ModelSerializer):
    department_id32 = serializers.SlugRelatedField(
        slug_field="id32",
        queryset=Department.objects.all(),
        source="department",
        required=False,
    )
    user_username = serializers.SlugRelatedField(
        slug_field="username", read_only=True, source="user"
    )
    user_full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    last_location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            "id32",
            "user_username",
            "department_id32",
            "user_full_name",
            "department_name",
            "last_location_coordinate",
            "basic_salary",
            "bank_account_number"
        )
        read_only_fields = ["id32", "user_full_name", "department_name"]

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_last_location_coordinate(self, obj):
        """
        Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute.
        """
        if obj.last_location:
            return {"latitude": obj.last_location.y, "longitude": obj.last_location.x}
        return None


class LocationTrackerSerializer(serializers.ModelSerializer):
    location_coordinate = serializers.SerializerMethodField()

    class Meta:
        model = LocationTracker
        fields = ["id32", "employee", "location", "location_coordinate", "created_at"]
        read_only_fields = ["id32", "employee", "created_at"]

    def create(self, validated_data):
        validated_data = handle_location(validated_data)
        return super().create(validated_data)

    def get_location_coordinate(self, obj):
        """Retrieve the geographic coordinates (latitude and longitude) from the given object's location attribute."""
        if obj.location:
            return {"latitude": obj.location.y, "longitude": obj.location.x}
        return None


class SalarySerializer(serializers.ModelSerializer):
    employee_id32 = serializers.CharField(write_only=True)
    user_username = serializers.SlugRelatedField(
        slug_field="username", read_only=True, source="employee.user"
    )
    user_full_name = serializers.SerializerMethodField()

    def get_user_full_name(self, instance):
        return instance.employee.user.get_full_name()

    def validate(self, attrs):
        employee_id32 = attrs.pop("employee_id32", None)
        pay_date = attrs["pay_date"]
        employee_instance = Employee.objects.filter(id32=employee_id32).last()
        if not employee_instance:
            raise serializers.ValidationError({"employee_id32": "invalid employee"})

        if not self.instance:
            exist_pay_date = Salary.objects.filter(
                pay_date=pay_date, employee=employee_instance
            ).exists()
            if exist_pay_date:
                raise serializers.ValidationError(
                    {"pay_date": "salary for pay date has already exists"}
                )

        attrs["employee"] = employee_instance

        return attrs

    class Meta:
        model = Salary
        fields = (
            "id32",
            "employee_id32",
            "user_username",
            "user_full_name",
            "salary",
            "pay_date",
            "incentive",
            "operational_cost",
            "bonus",
        )
        read_only_fields = ["id32", "user_full_name", "user_username"]


class SalaryReportSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()
    user_username = serializers.SlugRelatedField(
        slug_field="username", read_only=True, source="employee.user"
    )
    basic_salary = serializers.DecimalField(
        decimal_places=2, max_digits=19, source="employee.basic_salary"
    )
    bank_account_number = serializers.CharField(source="employee.bank_account_number")

    def get_user_full_name(self, instance):
        return instance.employee.user.get_full_name()

    class Meta:
        model = Salary
        fields = (
            "id32",
            "user_full_name",
            "user_username",
            "basic_salary",
            "bank_account_number",
            "salary",
            "pay_date",
            "incentive",
            "operational_cost",
            "bonus",
        )
