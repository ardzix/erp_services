from rest_framework import serializers
from ..models import UserProfile, CompanyProfile, Brand, File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

    class Meta:
        model = UserProfile
        fields = ['id', 'profile_picture', 'bio', 'contact_number']

class UserProfileDetailSerializer(serializers.ModelSerializer):
    profile_picture = FileSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'profile_picture', 'bio', 'contact_number']


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['id', 'company_name', 'address', 'contact_number']

class BrandSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=CompanyProfile.objects.all())

    class Meta:
        model = Brand
        fields = ['id', 'company', 'name', 'description']
