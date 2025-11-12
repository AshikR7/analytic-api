from rest_framework.permissions import BasePermission


class HasApiKey(BasePermission):
	def has_permission(self, request, view):
		# ApiKeyAuthentication attaches client_app if valid
		return hasattr(request, "client_app")


