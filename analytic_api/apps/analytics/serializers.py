from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = [
			"id",
			"event",
			"url",
			"referrer",
			"device",
			"ip_address",
			"timestamp",
			"metadata",
			"user_id",
		]
		read_only_fields = ["id"]


class EventSummaryQuerySerializer(serializers.Serializer):
	event = serializers.CharField()
	startDate = serializers.DateField(required=False)
	endDate = serializers.DateField(required=False)
	app_id = serializers.IntegerField(required=False)


class UserStatsQuerySerializer(serializers.Serializer):
	userId = serializers.CharField()


