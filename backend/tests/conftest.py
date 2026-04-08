import os

import pytest

os.environ.setdefault("ENV_FILE", "none")
os.environ.setdefault("CELERY_EAGER", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.pop("CELERY_BROKER_URL", None)
os.environ.pop("CELERY_RESULT_BACKEND", None)
os.environ.pop("REDIS_URL", None)
os.environ.pop("OPENAI_API_KEY", None)

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def env_setup(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CELERY_EAGER", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    monkeypatch.delenv("CELERY_RESULT_BACKEND", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    from app.main import app

    app.state.limiter.reset()
    from app.db import Base, engine

    Base.metadata.create_all(bind=engine)
    yield
    get_settings.cache_clear()
