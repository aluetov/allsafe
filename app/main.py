from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.db.db import create_database_engine, create_session_factory
from app.redis.redis import create_redis
from app.routers import auth, game, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine = create_database_engine(settings)

    app.state.settings = settings
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = create_redis(settings)

    try:
        yield
    finally:
        await engine.dispose()
        await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(game.router)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
