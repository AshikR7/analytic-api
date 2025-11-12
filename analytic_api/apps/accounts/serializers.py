from rest_framework import serializers
from .models import ClientApp


class ClientAppSerializer(serializers.ModelSerializer):
	class Meta:
		model = ClientApp
		fields = ["id", "name", "api_key", "is_revoked", "expires_at", "created_at", "updated_at"]
		read_only_fields = ["id", "api_key", "created_at", "updated_at"]


class RegisterAppSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=255)
	expires_in_days = serializers.IntegerField(required=False, min_value=1, max_value=365)


class RevokeSerializer(serializers.Serializer):
	app_id = serializers.IntegerField()


class RegenerateSerializer(serializers.Serializer):
	app_id = serializers.IntegerField()


