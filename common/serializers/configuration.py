from rest_framework import serializers
from ..models import Configuration

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ['key', 'value']

    def create(self, validated_data):
        return Configuration.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.key = validated_data.get('key', instance.key)
        instance.value = validated_data.get('value', instance.value)
        instance.save()
        return instance
