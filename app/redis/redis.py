import os

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

redis = Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True,
)