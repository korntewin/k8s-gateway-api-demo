from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional


@dataclass(frozen=True)
class RestSettings:
    api_key: Optional[str]
    uploads_mongodb_uri: str
    uploads_mongodb_database: str
    uploads_mongodb_collection: str


def _read_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is not None:
        return value
    return default


@lru_cache(maxsize=1)
def get_settings() -> RestSettings:
    return RestSettings(
        api_key=_read_env("APISERVER_API_KEY", "test-key"),
        uploads_mongodb_uri=_read_env("UPLOADS_MONGODB_URI", "mongodb://localhost:27017")
        or "mongodb://localhost:27017",
        uploads_mongodb_database=_read_env("UPLOADS_MONGODB_DATABASE", "uploads") or "uploads",
        uploads_mongodb_collection=_read_env("UPLOADS_MONGODB_COLLECTION", "records") or "records",
    )
