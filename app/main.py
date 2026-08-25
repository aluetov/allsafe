from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.redis.redis import create_redis
from app.routers import auth, scanner, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = create_redis()

    yield

    await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(scanner.router)
app.include_router(auth.router)
app.include_router(user.router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
