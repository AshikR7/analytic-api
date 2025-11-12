from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from apps.accounts.models import ClientApp


class ApiKeyAuthentication(BaseAuthentication):
	keyword = "X-API-KEY"

	def authenticate(self, request):
		api_key = request.headers.get(self.keyword)
		if not api_key:
			return None
		try:
			app = ClientApp.objects.get(api_key=api_key)
		except ClientApp.DoesNotExist:
			raise exceptions.AuthenticationFailed("Invalid API key.")
		if not app.is_active():
			raise exceptions.AuthenticationFailed("API key inactive.")
		# Attach app to request for later usage
		request.client_app = app
		# No user auth for ingestion; return (None, None) to mark as authenticated for permissions
		return (None, None)


