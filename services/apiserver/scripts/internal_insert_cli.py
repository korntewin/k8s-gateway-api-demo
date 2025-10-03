"""CLI helper for exercising the REST /internal-insert endpoint."""

import argparse
import json
import os
import random
import sys
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib import error, request

DEFAULT_BASE_URL = os.getenv("APISERVER_BASE_URL")
DEFAULT_API_KEY = os.getenv("APISERVER_API_KEY", "test-key")
DEFAULT_TIMEOUT = float(os.getenv("APISERVER_HTTP_TIMEOUT", "10"))


@dataclass(frozen=True)
class InsertResult:
    id: str
    score: float


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Insert random upload records via the REST internal-insert endpoint.",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=1,
        help="Number of documents to insert (default: 1)",
    )
    parser.add_argument(
        "-b",
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL for the REST API (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        default=DEFAULT_API_KEY,
        help="API key for the x-api-key header (default: value from APISERVER_API_KEY or 'test-key')",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds (default: value from APISERVER_HTTP_TIMEOUT or 10)",
    )
    return parser.parse_args(argv)


def _post_internal_insert(
    *,
    base_url: str,
    api_key: str | None,
    timeout: float,
    payload: Dict[str, Any],
) -> InsertResult:
    url = f"{base_url.rstrip('/')}/external-insert"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=data, headers=headers, method="POST")

    with request.urlopen(req, timeout=timeout) as resp:
        raw_body = resp.read()
    try:
        body = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise RuntimeError("Response was not valid JSON") from exc

    return InsertResult(id=str(body.get("id")), score=float(body.get("score", 0.0)))


def _build_payload() -> Dict[str, Any]:
    return {"id": str(uuid.uuid4()), "score": random.random()}


def main() -> None:
    args = _parse_args(sys.argv[1:])

    if args.count < 1:
        print("count must be a positive integer", file=sys.stderr)
        raise SystemExit(1)

    try:
        results = [
            _post_internal_insert(
                base_url=args.base_url,
                api_key=args.api_key,
                timeout=args.timeout,
                payload=_build_payload(),
            )
            for _ in range(args.count)
        ]
    except error.HTTPError as exc:
        print(f"HTTP error {exc.code} while inserting records: {exc.reason}", file=sys.stderr)
        try:
            detail = exc.read().decode("utf-8")
            if detail:
                print(detail, file=sys.stderr)
        except Exception:  # pragma: no cover - best effort logging
            pass
        raise SystemExit(1)
    except error.URLError as exc:
        print(f"Failed to reach REST API: {exc.reason}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # pragma: no cover - best effort logging
        print(f"Unexpected error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    for record in results:
        print(f"Inserted record id={record.id} score={record.score:.4f}")

    raise SystemExit(0)


if __name__ == "__main__":
    main()
