import phonenumbers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from phonenumbers import NumberParseException
from rest_framework import serializers


def normalize_phone_number(value: str) -> str:
    raw_phone = value.strip().replace(" ", "").replace("-", "")

    try:
        if raw_phone.startswith("+"):
            parsed_phone = phonenumbers.parse(raw_phone, None)
        else:
            parsed_phone = phonenumbers.parse(raw_phone, "IR")
    except NumberParseException:
        raise serializers.ValidationError(
            "Enter a valid phone number."
        )

    if not phonenumbers.is_valid_number(parsed_phone):
        raise serializers.ValidationError(
            "Enter a valid phone number."
        )

    return phonenumbers.format_number(
        parsed_phone,
        phonenumbers.PhoneNumberFormat.E164,
    )

def normalize_identifier(value: str) -> str:
    value = value.strip()

    if "@" in value:
        normalized_email = value.lower()

        try:
            validate_email(normalized_email)
        except DjangoValidationError:
            raise serializers.ValidationError(
                "Enter a valid email address."
            )

        return normalized_email

    return normalize_phone_number(value)
    

class RequestOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["login", "register"])

    def validate_identifier(self, value):
        return normalize_identifier(value)
    
    
class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["login", "register"])
    code = serializers.CharField()

    def validate_identifier(self, value):
        return normalize_identifier(value)

    def validate_code(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits.")

        if len(value) != 5:
            raise serializers.ValidationError("OTP code must be 5 digits.")

        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()