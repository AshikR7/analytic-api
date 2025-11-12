import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.accounts.models import ClientApp
from django.utils import timezone


@pytest.mark.django_db
def test_collect_and_summary_flow():
	owner = User.objects.create_user(username="owner", password="p1")
	app = ClientApp.objects.create(owner=owner, name="site1")
	collect = APIClient()
	# ingestion via API key header
	resp = collect.post(
		"/api/analytics/collect",
		{
			"event": "login_form_cta_click",
			"url": "https://example.com/page",
			"referrer": "https://google.com",
			"device": "mobile",
			"timestamp": timezone.now().isoformat(),
			"metadata": {"browser": "Chrome", "os": "Android"},
			"user_id": "user789",
		},
		format="json",
		HTTP_X_API_KEY=app.api_key,
	)
	assert resp.status_code == 201

	# analytics by owner
	client = APIClient()
	client.login(username="owner", password="p1")
	summary = client.get("/api/analytics/event-summary", {"event": "login_form_cta_click"})
	assert summary.status_code == 200
	assert summary.json()["count"] >= 1

	user_stats = client.get("/api/analytics/user-stats", {"userId": "user789"})
	assert user_stats.status_code == 200
	assert user_stats.json()["totalEvents"] >= 1


