from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjangoCoreValidationError
from django.contrib.auth.models import User
from rest_framework import serializers

class UsernamesField(serializers.RelatedField):
    def to_representation(self, value):
        return value.username

    def to_internal_value(self, data):
        try:
            return User.objects.get(username=data)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                f"User with username {data} does not exist.")