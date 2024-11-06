import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(hosts=[f"{settings.es_host}:{settings.es_port}"])
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    description="Информация о фильмах, жанрах и персонах.",
    docs_url="/api/openapi_movies",
    openapi_url="/api/openapi_movies.json",
    default_response_class=ORJSONResponse,
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(films.router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
