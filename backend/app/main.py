from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger import jsonlogger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.dialects.postgresql import insert as pg_insert
from starlette.responses import Response

from app.api.routes import router
from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.security import hash_password
from app.db import SessionLocal
from app.models import User

settings = get_settings()

logger = logging.getLogger()
logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter())
logger.addHandler(handler)
logger.setLevel(settings.log_level)

def _ensure_admin_user() -> None:
    if not settings.initial_admin_email or not settings.initial_admin_password:
        return
    db = SessionLocal()
    try:
        if db.bind and db.bind.dialect.name == "postgresql":
            stmt = (
                pg_insert(User)
                .values(
                    email=settings.initial_admin_email,
                    hashed_password=hash_password(settings.initial_admin_password),
                    role="admin",
                )
                .on_conflict_do_nothing(index_elements=["email"])
            )
            db.execute(stmt)
            db.commit()
        else:
            user = db.query(User).filter(User.email == settings.initial_admin_email).first()
            if not user:
                admin = User(
                    email=settings.initial_admin_email,
                    hashed_password=hash_password(settings.initial_admin_password),
                    role="admin",
                )
                db.add(admin)
                try:
                    db.commit()
                except Exception:
                    db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    _ensure_admin_user()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "API-first AI task automation platform with async workflows, "
        "real-time updates, and optional GPT-4 integration."
    ),
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

if settings.otlp_endpoint:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": "ai-task-automation"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otlp_endpoint))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
    except ImportError:
        logger.warning(
            "OpenTelemetry not installed; start without tracing. "
            "Install opentelemetry-instrumentation-fastapi to enable."
        )

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(router, prefix=settings.api_v1_prefix)
