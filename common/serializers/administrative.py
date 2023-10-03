from rest_framework import serializers
from ..models import AdministrativeLvl1, AdministrativeLvl2, AdministrativeLvl3, AdministrativeLvl4

class AdministrativeLvl1ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrativeLvl1
        fields = ['id', 'name']

class AdministrativeLvl2ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrativeLvl2
        fields = ['id', 'name', 'lvl1']

class AdministrativeLvl3ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrativeLvl3
        fields = ['id', 'name', 'lvl2']

class AdministrativeLvl4ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministrativeLvl4
        fields = ['id', 'name', 'lvl3']
