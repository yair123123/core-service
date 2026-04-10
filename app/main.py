from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.internal_call_routing import router as call_routing_router
from app.api.routes.internal_orders import router as internal_orders_router
from app.api.routes.internal_rides import router as internal_rides_router
from app.api.routes.stations import router as stations_router
from app.api.routes.version import router as version_router
from app.utils.logging import configure_logging

configure_logging()

app = FastAPI(title="core-service")
app.include_router(health_router)
app.include_router(version_router)
app.include_router(auth_router)
app.include_router(stations_router)
app.include_router(call_routing_router)
app.include_router(internal_orders_router)
app.include_router(internal_rides_router)
