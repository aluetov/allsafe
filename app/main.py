from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.db import create_tables
from .redis.redis import redis
from .routers import scanner


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()

    yield

    await redis.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(scanner.router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/redis")
async def redis_test():
    await redis.set("hello", "world")

    value = await redis.get("hello")

    return {"value": value}
