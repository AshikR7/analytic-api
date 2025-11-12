from django.db import models
from apps.accounts.models import ClientApp


class Event(models.Model):
	app = models.ForeignKey(ClientApp, on_delete=models.CASCADE, related_name="events")
	event = models.CharField(max_length=255, db_index=True)
	url = models.URLField(max_length=1000, blank=True)
	referrer = models.URLField(max_length=1000, blank=True)
	device = models.CharField(max_length=50, blank=True)
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	timestamp = models.DateTimeField(db_index=True)
	metadata = models.JSONField(default=dict, blank=True)
	user_id = models.CharField(max_length=255, blank=True, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=["app", "event", "timestamp"]),
			models.Index(fields=["app", "user_id"]),
		]


