"""Upload adapter backed by PyMongo's asyncio client."""

from dataclasses import dataclass
from typing import Any, List, Optional

from pymongo import AsyncMongoClient


@dataclass(frozen=True)
class UploadRecord:
    """Domain record stored by the upload adapter."""

    id: str
    score: float


class UploadAdapter:
    """Async MongoDB-backed persistence adapter for upload records."""

    def __init__(
        self,
        *,
        uri: str,
        database: str,
        collection_name: str,
    ) -> None:
        client = AsyncMongoClient[Any](uri)
        self._client = client
        self._collection = client[database][collection_name]

    async def upsert(self, record: UploadRecord) -> UploadRecord:
        """Insert or update a record using its id as the stable document key."""
        await self._collection.update_one(
            {"_id": record.id},
            {"$set": {"score": record.score}},
            upsert=True,
        )
        return record

    async def find_by_id(self, record_id: str) -> Optional[UploadRecord]:
        """Return a single record from MongoDB if it exists."""
        document = await self._collection.find_one({"_id": record_id})
        if document is None:
            return None
        return self._to_record(document)

    async def find_all(self) -> List[UploadRecord]:
        """Return all stored records."""
        cursor = self._collection.find({})
        return [self._to_record(document) async for document in cursor]

    async def close(self) -> None:
        """Close the underlying MongoDB client if this adapter created it."""
        if getattr(self, "_owns_client", False) and getattr(self, "_client", None) is not None:
            await self._client.close()  # type: ignore[func-returns-value]

    @staticmethod
    def _to_record(document: Any) -> UploadRecord:
        return UploadRecord(
            id=str(document.get("_id")),
            score=float(document.get("score", 0.0)),
        )
