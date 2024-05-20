from rest_framework import serializers
from django.contrib.auth.models import User, Group


USER_FIELDS = [
    "id",
    "first_name",
    "last_name",
    "email",
    "date_joined"
]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            "id",
            "name"
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = USER_FIELDS


class UserGroupSerializer(UserSerializer):
    groups = serializers.SerializerMethodField()

    def get_groups(self, instance):
        groups = instance.groups.filter()
        if not groups.exists():
            return []
        return GroupSerializer(groups, many=True).data

    class Meta:
        model = User
        fields = USER_FIELDS + ["groups"]


class SetGroupSerializer(serializers.Serializer):
    group_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False)

    def validate_group_ids(self, group_ids):
        valid_groups = Group.objects.filter(id__in=group_ids)
        valid_group_ids = set(valid_groups.values_list('id', flat=True))
        invalid_group_ids = set(group_ids) - valid_group_ids

        if invalid_group_ids:
            invalid_ids = ", ".join(map(str, invalid_group_ids))
            raise serializers.ValidationError(
                f"The following group IDs are invalid: {invalid_ids}. Please check and try again.")

        return valid_groups
