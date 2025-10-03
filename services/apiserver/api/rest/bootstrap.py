from functools import cache

from apiserver.api.rest.config import get_settings
from apiserver.services.adapters.upload_adapter import UploadAdapter
from apiserver.services.upload_service import UploadService


@cache
def get_upload_service() -> UploadService:
    settings = get_settings()
    adapter = UploadAdapter(
        uri=settings.uploads_mongodb_uri,
        database=settings.uploads_mongodb_database,
        collection_name=settings.uploads_mongodb_collection,
    )
    return UploadService(adapter=adapter)
