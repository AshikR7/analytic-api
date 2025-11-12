from rest_framework.throttling import SimpleRateThrottle


class CollectThrottle(SimpleRateThrottle):
	scope = "collect"

	def get_cache_key(self, request, view):
		api_key = request.headers.get("X-API-KEY")
		if not api_key:
			return None
		return self.cache_format % {"scope": self.scope, "ident": api_key}


class AnalyticsThrottle(SimpleRateThrottle):
	scope = "analytics"

	def get_cache_key(self, request, view):
		ident = self.get_ident(request)
		return self.cache_format % {"scope": self.scope, "ident": ident}


