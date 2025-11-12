from django.urls import path
from .views import RegisterView, ApiKeyView, RevokeView, RegenerateView

urlpatterns = [
	path("register", RegisterView.as_view()),
	path("api-key", ApiKeyView.as_view()),
	path("revoke", RevokeView.as_view()),
	path("regenerate", RegenerateView.as_view()),
]


