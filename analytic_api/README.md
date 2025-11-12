## Website Analytics API (Django REST)

Scalable backend API for collecting analytics events and generating summaries. Includes API key management, rate limiting, caching with Redis, Swagger docs, tests, and Docker support.

### Features
- API Key Management: register, list, revoke, regenerate
- Event Collection: POST `/api/analytics/collect` with `X-API-KEY`
- Analytics: event summary and user stats with Redis caching
- Rate limiting: fast protection for collect and analytics endpoints
- Swagger Docs: `/api/docs`
- Dockerized with SQLite (default) + Redis

### Quick Start (Docker)
1. Copy env: create `.env` from variables in `docker-compose.yml` if needed.
2. Run:
```bash
docker compose up --build
```
3. Open:
 - API Docs: http://localhost:8000/api/docs
 - Schema: http://localhost:8000/api/schema/

### Local Dev
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DB_VENDOR="sqlite"  # default; switch to postgres if needed
export REDIS_URL or run docker compose for services
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Endpoints
- POST `/api/auth/register` (auth required): body `{ "name": "My App", "expires_in_days": 30? }`
- GET `/api/auth/api-key` (auth required): list API keys
- POST `/api/auth/revoke` (auth required): `{ "app_id": 1 }`
- POST `/api/auth/regenerate` (auth required): `{ "app_id": 1 }`
- Swap `DB_VENDOR=postgres` in env to use Postgres; defaults to SQLite for local quickstart.
- Without `REDIS_URL`, project falls back to local in-memory caching.

- POST `/api/analytics/collect` (header `X-API-KEY` required):
```json
{
  "event": "login_form_cta_click",
  "url": "https://example.com/page",
  "referrer": "https://google.com",
  "device": "mobile",
  "ip_address": "1.2.3.4",
  "timestamp": "2024-02-20T12:34:56Z",
  "metadata": { "browser": "Chrome", "os": "Android", "screenSize": "1080x1920" },
  "user_id": "user789"
}
```

- GET `/api/analytics/event-summary` (auth required): query `event`, optional `startDate`, `endDate`, `app_id`
- GET `/api/analytics/user-stats` (auth required): query `userId`

### Google Auth
For production, integrate Google OAuth using `django-allauth` or a gateway (e.g., Auth0). This project authenticates with Django users for simplicity and keeps a switch `ENABLE_GOOGLE_AUTH` in settings for future enablement.

### Tests
```bash
pytest -q
```

### Deployment
- Build image and deploy to Render/Railway/Heroku
- Ensure environment variables set: `POSTGRES_*`, `REDIS_URL`, `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`
- Point to `/api/docs` for Swagger

### Notes / Future Work
- Add Google OAuth (django-allauth)
- Add partitioning/time-series optimizations for events table
- Add background pipeline for heavy aggregations
- Expand analytics endpoints (time series, per-url, per-referrer)


