# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Department, Employee

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id32', 'name']
        read_only_fields = ['id32']

class EmployeeSerializer(serializers.ModelSerializer):
    department_id32 = serializers.SlugRelatedField(
        slug_field='id32',
        queryset=Department.objects.all(),
        source='department',
        required=False
    )
    user_username = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        source='user'
    )
    user_full_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ('id32', 'user_username', 'department_id32', 'user_full_name', 'department_name')
        read_only_fields = ['id32', 'user_full_name', 'department_name']

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None