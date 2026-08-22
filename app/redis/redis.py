from fastapi import Request
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


def create_redis() -> Redis:
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
    )


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
