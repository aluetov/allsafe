from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import scanner
from .db.db import create_tables
from .redis.redis import redis

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_tables()
    await redis.ping()
    print("Redis connected")

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