from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self, redis_url: Optional[str], channel: str) -> None:
        self.redis_url = redis_url
        self.channel = channel
        self._redis: Optional[redis.Redis] = None

    async def connect(self) -> None:
        if not self.redis_url:
            return
        self._redis = redis.from_url(self.redis_url)
        try:
            await self._redis.ping()
        except Exception:
            logger.warning("Redis not available for event bus.")
            self._redis = None

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()

    async def publish(self, payload: Dict[str, Any]) -> None:
        if not self._redis:
            return
        await self._redis.publish(self.channel, json.dumps(payload))

    async def subscribe(self) -> AsyncGenerator[Dict[str, Any], None]:
        if not self._redis:
            return

        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self.channel)
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                data = message.get("data")
                if not data:
                    continue
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    logger.warning("Received malformed event.")
        finally:
            await pubsub.unsubscribe(self.channel)
            await pubsub.close()

    @property
    def is_active(self) -> bool:
        return self._redis is not None


_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus:
        return _event_bus

    settings = get_settings()
    _event_bus = EventBus(settings.redis_url, settings.event_channel)
    return _event_bus
