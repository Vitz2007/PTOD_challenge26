import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import health, stations
from app.cache import TTLCache
from app.config import Settings, get_settings
from app.odpt.client import ODPTClient, ODPTError
from app.services.stations import StationService

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # One HTTP client for the whole app, so connections to ODPT are reused
        async with httpx.AsyncClient(base_url=settings.odpt_base_url, timeout=settings.odpt_timeout_seconds) as http:
            client = ODPTClient(http, settings.odpt_consumer_key)
            app.state.station_service = StationService(client, TTLCache(), settings)
            yield

    app = FastAPI(
        title="Low-burden Mode Accessibility API",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["GET"], allow_headers=["*"])

    @app.exception_handler(ODPTError)
    async def odpt_error(request: Request, exc: ODPTError):
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    app.include_router(health.router, prefix="/api")
    app.include_router(stations.router, prefix="/api/v1")

    # Serve the built React app at / (after `npm run build` in frontend/)
    if settings.frontend_dist.exists():
        app.mount("/", StaticFiles(directory=settings.frontend_dist, html=True), name="frontend")
    else:
        logger.info("No frontend build at %s; serving the API only", settings.frontend_dist)

    return app


app = create_app()
