from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from ..models import Unit

class UnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id32', 'name', 'symbol']

class UnitDetailSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()  # to get parent unit's id32

    class Meta:
        model = Unit
        fields = ['id32', 'name', 'symbol', 'parent', 'conversion_factor', 'level']

    def get_parent(self, obj):
        return obj.parent.id32 if obj.parent else None

class UnitCreateUpdateSerializer(serializers.ModelSerializer):
    parent_id32 = serializers.IntegerField(source='parent_id', allow_null=True, required=False)

    class Meta:
        model = Unit
        fields = ['id32', 'name', 'symbol', 'parent_id32', 'conversion_factor']
        read_only_fields = ['id32']

    def validate_parent_id32(self, value):
        try:
            parent_unit = Unit.objects.get(id32=value)
            return parent_unit.id
        except Unit.DoesNotExist:
            raise serializers.ValidationError({
                'parent_id32': _('The provided id32 for the parent unit does not exist.')
            })
