from rest_framework import serializers

class RequestOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["login", "register"])