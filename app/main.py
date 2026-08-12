from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from redis.asyncio import Redis

from .db.db import create_tables
from .redis.redis import create_redis, get_redis
from .routers import scanner


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    app.state.redis = create_redis()

    yield

    await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(scanner.router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/redis")
async def redis_test(redis: Annotated[Redis, Depends(get_redis)]):
    await redis.set("hello", "world")

    value = await redis.get("hello")

    return {"value": value}
