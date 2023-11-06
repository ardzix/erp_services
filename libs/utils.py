from rest_framework import serializers
from common.models import File, Configuration

TRUE = ['true', 'True', 1, True]

def get_config_value(key):
    try:
        return Configuration.objects.get(key=key).value
    except Configuration.DoesNotExist:
        return None


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
    

def handle_file_fields(validated_data, fields):
    """
    Handle file fields in the validated data.

    Parameters:
    - validated_data (dict): The data validated by the serializer.
    - fields (dict): The mapping of the field name in validated data to its model name.

    Returns:
    - dict: The validated data with file fields mapped to their respective models.
    """
    for field_name, model_name in fields.items():
        if field_name in validated_data:
            file_object = validated_data.pop(field_name)
            validated_data[model_name] = file_object
    return validated_data