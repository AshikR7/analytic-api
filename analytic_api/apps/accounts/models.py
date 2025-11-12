import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ClientApp(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_apps")
	name = models.CharField(max_length=255)
	api_key = models.CharField(max_length=64, unique=True, db_index=True)
	is_revoked = models.BooleanField(default=False)
	expires_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.api_key:
			self.api_key = secrets.token_hex(24)
		super().save(*args, **kwargs)

	def is_active(self) -> bool:
		if self.is_revoked:
			return False
		if self.expires_at and timezone.now() > self.expires_at:
			return False
		return True

	def regenerate_api_key(self):
		self.api_key = secrets.token_hex(24)
		self.save(update_fields=["api_key", "updated_at"])


