from datetime import timedelta
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import ClientApp
from .serializers import ClientAppSerializer, RegisterAppSerializer, RevokeSerializer, RegenerateSerializer


class RegisterView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(
		request=RegisterAppSerializer,
		responses=ClientAppSerializer,
		description="Register a new client application and issue an API key.",
	)
	def post(self, request):
		serializer = RegisterAppSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		name = serializer.validated_data["name"]
		expires_in_days = serializer.validated_data.get("expires_in_days")
		expires_at = None
		if expires_in_days:
			expires_at = timezone.now() + timedelta(days=expires_in_days)
		app = ClientApp.objects.create(owner=request.user, name=name, expires_at=expires_at)
		return Response(ClientAppSerializer(app).data, status=status.HTTP_201_CREATED)


class ApiKeyView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(
		responses=ClientAppSerializer(many=True),
		description="List active API keys for the authenticated user.",
	)
	def get(self, request):
		apps = ClientApp.objects.filter(owner=request.user, is_revoked=False)
		return Response(ClientAppSerializer(apps, many=True).data)


class RevokeView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(
		request=RevokeSerializer,
		responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
		description="Revoke the specified API key.",
	)
	def post(self, request):
		serializer = RevokeSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		app_id = serializer.validated_data["app_id"]
		try:
			app = ClientApp.objects.get(id=app_id, owner=request.user)
		except ClientApp.DoesNotExist:
			return Response({"detail": "App not found."}, status=status.HTTP_404_NOT_FOUND)
		app.is_revoked = True
		app.save(update_fields=["is_revoked", "updated_at"])
		return Response({"detail": "API key revoked."})


class RegenerateView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	@extend_schema(
		request=RegenerateSerializer,
		responses=ClientAppSerializer,
		description="Regenerate a new API key for the specified application.",
	)
	def post(self, request):
		serializer = RegenerateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		app_id = serializer.validated_data["app_id"]
		try:
			app = ClientApp.objects.get(id=app_id, owner=request.user)
		except ClientApp.DoesNotExist:
			return Response({"detail": "App not found."}, status=status.HTTP_404_NOT_FOUND)
		app.regenerate_api_key()
		return Response(ClientAppSerializer(app).data)


