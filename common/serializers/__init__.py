import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from ..models import File
from django.contrib.auth.models import User
from rest_framework import serializers

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

class SetFileSerializer(serializers.Serializer):
    file_base64 = serializers.CharField(write_only=True, help_text="Base64 encoded file data")

    def create(self, validated_data):
        encoded_file = validated_data['file_base64']
        file_format, imgstr = encoded_file.split(';base64,') 
        user = self.context.get('request').user
        ext = file_format.split('/')[-1]
        
        # Add padding if required
        missing_padding = len(imgstr) % 4
        if missing_padding:
            imgstr += '=' * (4 - missing_padding)
            
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        # Create File instance
        file_instance = File.objects.create(name=data.name, file=data, created_by=user)
        return file_instance