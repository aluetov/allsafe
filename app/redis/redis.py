import os

from fastapi import Request
from redis.asyncio import Redis


def create_redis() -> Redis:
    return Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=True,
    )


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
