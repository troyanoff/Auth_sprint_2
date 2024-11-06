import os
import uvicorn

from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from api.v1 import users, roles, auth
from core.config import settings
from db import redis


def configure_tracer() -> None:
    resource = Resource(attributes={"service.name": "auth_service"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    jaeger_url = f"http://{settings.jaeger_host}:{settings.jaeger_port}"
    otlp_exporter = OTLPSpanExporter(endpoint=jaeger_url, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await FastAPILimiter.init(redis.redis)
    # Раскомментить для локального запуска.
    # os.system('alembic revision --autogenerate -m "Initial tables"')
    # os.system('alembic upgrade head')
    # os.system('python3 create_superuser.py')
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    description="Информация о фильмах, жанрах и персонах.",
    docs_url="/api/openapi_auth",
    openapi_url="/api/openapi_auth.json",
    default_response_class=ORJSONResponse,
    version="1.0.0",
    lifespan=lifespan,
)

if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    return response


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(users.router, prefix="/api/v1/users", tags=["Пользователи"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Роли"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Авторизация"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
