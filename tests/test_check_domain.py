import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.routers import scanner


@pytest.mark.asyncio
async def test_check_domain_redis_hit(monkeypatch):
    cached_data = {
        "qname": "example.com.",
        "canonical_name": "example.com.",
        "record_type": "A",
        "record_class": "IN",
        "expiration": 123456.0,
        "records": ["93.184.216.34"],
    }

    redis_get = AsyncMock(return_value=json.dumps(cached_data))
    redis_ttl = AsyncMock(return_value=250)

    monkeypatch.setattr(scanner.redis, "get", redis_get)
    monkeypatch.setattr(scanner.redis, "ttl", redis_ttl)

    response = await scanner.check_domain("example.com")

    assert response == {
        "source": "redis",
        "ttl": 250,
        "cached_response": cached_data,
    }

@pytest.mark.asyncio
async def test_check_domain_postgres_hit(monkeypatch):
    monkeypatch.setattr(
        scanner.redis,
        "get",
        AsyncMock(return_value=None),
    )

    redis_set = AsyncMock()
    monkeypatch.setattr(scanner.redis, "set", redis_set)

    db_domain = MagicMock()
    db_domain.qname = "example.com."
    db_domain.canonical_name = "example.com."
    db_domain.record_type = "A"
    db_domain.record_class = "IN"
    db_domain.expiration = 123456.0
    db_domain.records = ["93.184.216.34"]

    scalar_result = MagicMock()
    scalar_result.first.return_value = db_domain

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalar_result

    session = AsyncMock()
    session.execute.return_value = execute_result

    session_context = AsyncMock()
    session_context.__aenter__.return_value = session
    session_context.__aexit__.return_value = None

    session_factory = MagicMock()
    session_factory.begin.return_value = session_context

    monkeypatch.setattr(scanner, "Session", session_factory)

    response = await scanner.check_domain("example.com")

    expected_data = {
        "qname": "example.com.",
        "canonical_name": "example.com.",
        "record_type": "A",
        "record_class": "IN",
        "expiration": 123456.0,
        "records": ["93.184.216.34"],
    }

    assert response == {
        "source": "postgres",
        "data": expected_data,
    }

    redis_set.assert_awaited_once_with(
        "dns:example.com",
        json.dumps(expected_data),
        ex=300,
    )

@pytest.mark.asyncio
async def test_check_domain_not_found(monkeypatch):
    monkeypatch.setattr(
        scanner.redis,
        "get",
        AsyncMock(return_value=None),
    )

    scalar_result = MagicMock()
    scalar_result.first.return_value = None

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalar_result

    session = AsyncMock()
    session.execute.return_value = execute_result

    session_context = AsyncMock()
    session_context.__aenter__.return_value = session
    session_context.__aexit__.return_value = None

    session_factory = MagicMock()
    session_factory.begin.return_value = session_context

    monkeypatch.setattr(scanner, "Session", session_factory)

    with pytest.raises(HTTPException) as exc_info:
        await scanner.check_domain("missing.com")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Domain not found"