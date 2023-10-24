from rest_framework import serializers
from common.models import File

def validate_file_by_id32(value, error_message):
    """
    Helper method to validate file existence by its id32.

    Parameters:
    - value (str): The id32 of the file to be validated.
    - error_message (str): The error message template to be returned if validation fails.

    Returns:
    - File instance: The File instance if found.

    Raises:
    - serializers.ValidationError: If the file with the given id32 does not exist.
    """
    if not value:
        return value

    try:
        file = File.objects.get(id32=value)
        return file
    except File.DoesNotExist:
        raise serializers.ValidationError(
            error_message.format(value=value))