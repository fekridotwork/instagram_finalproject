from rest_framework import serializers


class RequestOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["login", "register"])

    def validate_identifier(self, value):
        value = value.strip()

        if "@" in value:
            return value.lower()

        if value.isdigit() and len(value) >= 10:
            return value

        raise serializers.ValidationError("Identifier must be a valid email or phone number.")


class VerifyOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["login", "register"])
    code = serializers.CharField()

    def validate_code(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits.")

        if len(value) != 5:
            raise serializers.ValidationError("OTP code must be 5 digits.")

        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()