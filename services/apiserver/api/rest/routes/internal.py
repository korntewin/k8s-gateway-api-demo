from dataclasses import asdict
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apiserver.api.rest.bootstrap import get_upload_service
from apiserver.services.adapters.upload_adapter import UploadRecord
from apiserver.services.upload_service import UploadService

router = APIRouter()


class InternalInsertRequest(BaseModel):
    id: str = Field(..., min_length=1, description="Unique identifier for the record")
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1 inclusive")


class InternalInsertResponse(BaseModel):
    id: str
    score: float


class InternalReadResponse(BaseModel):
    id: str
    score: float


@router.post("/internal-insert", response_model=InternalInsertResponse)
async def internal_insert(
    payload: InternalInsertRequest,
    service: UploadService = Depends(get_upload_service),
) -> InternalInsertResponse:
    try:
        record = await service.internal_insert(UploadRecord(id=payload.id, score=payload.score))
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return InternalInsertResponse.model_validate(asdict(record))


@router.get("/internal-read", response_model=List[InternalReadResponse])
async def internal_read(
    record_id: Optional[str] = Query(None, alias="id", description="Filter by record id"),
    service: UploadService = Depends(get_upload_service),
) -> List[InternalReadResponse]:
    records = await service.internal_read(record_id=record_id)
    return [InternalReadResponse.model_validate(asdict(record)) for record in records]
