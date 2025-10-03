"""Dagster job wiring the Mongo extraction and Delta write ops."""

import json

from dagster import Definitions, job  # type: ignore
from dagster_k8s.job import USER_DEFINED_K8S_CONFIG_KEY

from dagster_service.src import config
from dagster_service.src.ops import fetch_upload_records, write_delta_table
from dagster_service.src.resources import mongo_collection_resource


def _k8s_job_tags() -> dict[str, str]:
    """Encode raw K8s job spec tweaks (like TTL) into Dagster tags."""
    ttl_seconds = config.dagster_job_ttl_seconds()
    job_spec = {"ttl_seconds_after_finished": ttl_seconds}

    return {USER_DEFINED_K8S_CONFIG_KEY: json.dumps({"job_spec_config": job_spec})}


@job(
    name="mongo_to_delta",
    resource_defs={"mongo_collection": mongo_collection_resource },
    tags=_k8s_job_tags(),
)
def mongo_to_delta_job() -> None:
    write_delta_table(fetch_upload_records())


defs = Definitions(
    jobs=[mongo_to_delta_job],
)
