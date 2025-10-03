from typing import List, Optional

from apiserver.services.adapters.upload_adapter import UploadAdapter, UploadRecord


class UploadService:
    """Business logic for handling upload records."""

    def __init__(self, adapter: UploadAdapter) -> None:
        self._adapter = adapter

    async def internal_insert(self, record: UploadRecord) -> UploadRecord:
        """Validate and upsert a record."""
        self._validate_score(record.score)
        return await self._adapter.upsert(record)

    async def internal_read(self, record_id: Optional[str] = None) -> List[UploadRecord]:
        """Return all records or a single record wrapped in a list."""
        if record_id:
            record = await self._adapter.find_by_id(record_id)
            return [record] if record else []
        return await self._adapter.find_all()

    @staticmethod
    def _validate_score(score: float) -> None:
        if not 0.0 <= score <= 1.0:
            raise ValueError("score must be between 0 and 1 inclusive")
