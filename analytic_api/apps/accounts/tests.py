import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_and_get_api_key():
	user = User.objects.create_user(username="u1", password="p1")
	client = APIClient()
	client.login(username="u1", password="p1")
	resp = client.post("/api/auth/register", {"name": "My App"}, format="json")
	assert resp.status_code == 201
	resp2 = client.get("/api/auth/api-key")
	assert resp2.status_code == 200
	assert len(resp2.json()) == 1


