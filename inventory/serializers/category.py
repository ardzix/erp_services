from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from ..models import Category

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id32', 'name']

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id32', 'name', 'description']
        read_only_fields = ['id32']