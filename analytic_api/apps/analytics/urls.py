from django.urls import path
from .views import CollectEventView, EventSummaryView, UserStatsView

urlpatterns = [
	path("collect", CollectEventView.as_view()),
	path("event-summary", EventSummaryView.as_view()),
	path("user-stats", UserStatsView.as_view()),
]


