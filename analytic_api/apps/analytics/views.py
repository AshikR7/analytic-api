from datetime import datetime, timedelta
from django.db.models import Count
from django.utils.dateparse import parse_datetime
from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import Event
from .serializers import EventSerializer, EventSummaryQuerySerializer, UserStatsQuerySerializer
from .auth import ApiKeyAuthentication
from .permissions import HasApiKey
from .throttles import CollectThrottle, AnalyticsThrottle


class CollectEventView(APIView):
	authentication_classes = [ApiKeyAuthentication]
	permission_classes = [HasApiKey]
	throttle_classes = [CollectThrottle]

	@extend_schema(
		parameters=[
			OpenApiParameter(
				name="X-API-KEY",
				required=True,
				type=OpenApiTypes.STR,
				location=OpenApiParameter.HEADER,
				description="API key generated via /api/auth/register.",
			)
		],
		request=EventSerializer,
		responses={201: {"type": "object", "properties": {"detail": {"type": "string"}}}},
		description="Collect an analytics event. Requires X-API-KEY header.",
	)
	def post(self, request):
		data = request.data.copy()
		# Default timestamp to now if not provided
		if "timestamp" in data and isinstance(data["timestamp"], str):
			# Ensure ISO string to datetime
			try:
				ts = parse_datetime(data["timestamp"])
				if ts is None:
					return Response({"detail": "Invalid timestamp."}, status=status.HTTP_400_BAD_REQUEST)
				data["timestamp"] = ts
			except Exception:
				return Response({"detail": "Invalid timestamp."}, status=status.HTTP_400_BAD_REQUEST)
		else:
			data["timestamp"] = datetime.utcnow()
		# capture IP if not provided
		if not data.get("ip_address"):
			data["ip_address"] = request.META.get("REMOTE_ADDR")
		serializer = EventSerializer(data=data)
		serializer.is_valid(raise_exception=True)
		Event.objects.create(app=request.client_app, **serializer.validated_data)
		return Response({"detail": "Event accepted."}, status=status.HTTP_201_CREATED)


class EventSummaryView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	throttle_classes = [AnalyticsThrottle]

	@extend_schema(
		parameters=[
			OpenApiParameter("event", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Event name", required=True),
			OpenApiParameter("startDate", OpenApiTypes.DATE, OpenApiParameter.QUERY, description="Start date filter"),
			OpenApiParameter("endDate", OpenApiTypes.DATE, OpenApiParameter.QUERY, description="End date filter"),
			OpenApiParameter("app_id", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Specific app id"),
		],
		responses={
			200: OpenApiTypes.OBJECT,
		},
		description="Retrieve aggregated stats for an event.",
	)
	def get(self, request):
		query_serializer = EventSummaryQuerySerializer(data=request.query_params)
		query_serializer.is_valid(raise_exception=True)
		event = query_serializer.validated_data["event"]
		start_date = query_serializer.validated_data.get("startDate")
		end_date = query_serializer.validated_data.get("endDate")
		app_id = query_serializer.validated_data.get("app_id")

		# Cache key
		cache_key = f"event-summary:{request.user.id}:{event}:{start_date}:{end_date}:{app_id}"
		cached = cache.get(cache_key)
		if cached:
			return Response(cached)

		qs = Event.objects.filter(event=event, app__owner=request.user)
		if app_id:
			qs = qs.filter(app_id=app_id)
		if start_date:
			qs = qs.filter(timestamp__date__gte=start_date)
		if end_date:
			qs = qs.filter(timestamp__date__lte=end_date)

		count = qs.count()
		unique_users = qs.exclude(user_id="").values("user_id").distinct().count()
		device_counts = qs.values("device").annotate(c=Count("id"))
		device_data = {row["device"] or "unknown": row["c"] for row in device_counts}

		resp = {
			"event": event,
			"count": count,
			"uniqueUsers": unique_users,
			"deviceData": device_data,
		}
		cache.set(cache_key, resp, timeout=60)  # cache for 60s
		return Response(resp)


class UserStatsView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	throttle_classes = [AnalyticsThrottle]

	@extend_schema(
		parameters=[
			OpenApiParameter("userId", OpenApiTypes.STR, OpenApiParameter.QUERY, description="User identifier", required=True),
		],
		responses={
			200: OpenApiTypes.OBJECT,
		},
		description="Fetch per-user stats such as total events and latest device info.",
	)
	def get(self, request):
		query_serializer = UserStatsQuerySerializer(data=request.query_params)
		query_serializer.is_valid(raise_exception=True)
		user_id = query_serializer.validated_data["userId"]
		cache_key = f"user-stats:{request.user.id}:{user_id}"
		cached = cache.get(cache_key)
		if cached:
		 return Response(cached)

		qs = Event.objects.filter(app__owner=request.user, user_id=user_id)
		total = qs.count()
		latest = qs.order_by("-timestamp").first()
		device_details = {}
		ip_address = None
		if latest:
			md = latest.metadata or {}
			device_details = {
				"browser": md.get("browser"),
				"os": md.get("os"),
			}
			ip_address = latest.ip_address
		resp = {
			"userId": user_id,
			"totalEvents": total,
			"deviceDetails": device_details,
			"ipAddress": ip_address,
		}
		cache.set(cache_key, resp, timeout=60)
		return Response(resp)


