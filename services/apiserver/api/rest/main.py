from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from apiserver.api.rest.config import get_settings
from apiserver.api.rest.routes.internal import router

api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_header(api_key: str | None = Security(api_key_scheme)) -> None:
    settings = get_settings()
    expected_key = settings.api_key
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def create_app() -> FastAPI:
    app = FastAPI(title="apiserver")
    app.include_router(router, dependencies=[Depends(verify_header)])
    return app


app = create_app()


@app.get("/")
async def health():
    return {"msg": "OK"}
