from rest_framework import serializers
from common.serializers import FileSerializer
from ..models import UserProfile, CompanyProfile, Brand, File

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id32', 'profile_picture', 'bio', 'contact_number']

    def get_profile_picture(self, object):
        return object.picture.file.url if object.picture and object.picture.file else None

class UserProfileDetailSerializer(serializers.ModelSerializer):
    profile_picture = FileSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id32', 'profile_picture', 'bio', 'contact_number']


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['id32', 'company_name', 'address', 'contact_number']

class BrandSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=CompanyProfile.objects.all())

    class Meta:
        model = Brand
        fields = ['id32', 'company', 'name', 'description']
