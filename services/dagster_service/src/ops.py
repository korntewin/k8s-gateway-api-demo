"""Dagster ops for moving Mongo upload records into Delta Lake."""

from typing import Any, Dict, List

from apiserver.services.adapters.upload_adapter import UploadRecord
from dagster import In, Nothing, OpExecutionContext, Out, op


def _to_record(document: Dict[str, object]) -> UploadRecord:
    return UploadRecord(
        id=str(document.get("_id")),
        score=float(document.get("score", 0.0)),  # type: ignore
    )


@op(required_resource_keys={"mongo_collection"}, out=Out(List[Dict[str, Any]]))
def fetch_upload_records(context: OpExecutionContext) -> List[Dict[str, Any]]:
    """Pull all upload records from MongoDB as serialisable dicts."""
    documents = list(context.resources.mongo_collection.find({}))
    records = [_to_record(document) for document in documents]
    context.log.info("Fetched %s records from MongoDB", len(records))
    context.log.debug("Fetched records: %s", records)
    return [  # type: ignore
        {
            "id": record.id,
            "score": record.score,
        }
        for record in records
    ]


@op(ins={"records": In(List[Dict[str, Any]])}, out=Out(Nothing))
def write_delta_table(context: OpExecutionContext, records: List[Dict[str, Any]]) -> None:
    """Write the provided records to the Delta Lake table."""
    if not records:
        context.log.info("No records to write; skipping Delta Lake materialisation")
        return

    context.log.info(f"Mock writing data to Delta Table with number of records = {len(records)}")
