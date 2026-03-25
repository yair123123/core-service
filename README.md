# core-service

Internal business backend for taxi-by-phone call flows. The telephony service asks this service how to route callers and manages rides through internal APIs.

## Tech stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2 / pydantic-settings
- Alembic
- SQLite (local), PostgreSQL-ready via `CORE_SERVICE_DATABASE_URL`

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Environment variables
- `CORE_SERVICE_DATABASE_URL` (default `sqlite:///./core_service.db`)
- `CORE_SERVICE_FIXED_CITY_RIDE_PRICE` (default `25.0`)
- `CORE_SERVICE_ENVIRONMENT` (default `dev`)

## Tests
```bash
pytest -q
```

## Internal APIs

### Health
```bash
curl http://localhost:8000/health
```

### Resolve call routing
```bash
curl -X POST http://localhost:8000/internal/call-routing/resolve \
  -H 'Content-Type: application/json' \
  -d '{"phone":"0521234567"}'
```

### Process call order
```bash
curl -X POST http://localhost:8000/internal/orders/process-call-order \
  -H 'Content-Type: application/json' \
  -d '{
    "callSessionId":"abc",
    "fromPhone":"0521234567",
    "originRecordingUrl":"https://example.com/o",
    "destinationRecordingUrl":"https://example.com/d",
    "notesRecordingUrl":"https://example.com/n"
  }'
```

### Confirm ride
```bash
curl -X POST http://localhost:8000/internal/rides/1/confirm
```

### Cancel searching by customer phone
```bash
curl -X POST http://localhost:8000/internal/rides/by-customer/0521234567/cancel-searching
```
