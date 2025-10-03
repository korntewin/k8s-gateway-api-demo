"""Configuration helpers for the Dagster service."""

import os
from dataclasses import dataclass
from typing import Tuple

UPLOADS_MONGODB_URI_ENV = "UPLOADS_MONGODB_URI"
UPLOADS_MONGODB_DATABASE_ENV = "UPLOADS_MONGODB_DATABASE"
UPLOADS_MONGODB_COLLECTION_ENV = "UPLOADS_MONGODB_COLLECTION"
DELTA_LAKE_OUTPUT_PATH_ENV = "DELTA_LAKE_OUTPUT_PATH"
MINIO_ENDPOINT_ENV = "MINIO_ENDPOINT"
MINIO_ACCESS_KEY_ENV = "MINIO_ACCESS_KEY"
MINIO_SECRET_KEY_ENV = "MINIO_SECRET_KEY"
SPARK_LOG_LEVEL_ENV = "SPARK_LOG_LEVEL"
SPARK_MASTER_URL_ENV = "SPARK_MASTER_URL"
SPARK_JARS_PACKAGES_ENV = "SPARK_JARS_PACKAGES"
DAGSTER_JOB_TTL_SECONDS_ENV = "DAGSTER_JOB_TTL_SECONDS"

DEFAULT_MONGO_URI = "mongodb://mongodb-mongodb-svc.mongodb-cluster.svc.cluster.local:27017"
DEFAULT_MONGO_DATABASE = "uploads"
DEFAULT_MONGO_COLLECTION = "records"
DEFAULT_DELTA_OUTPUT_PATH = "s3a://deltalake/uploads"
DEFAULT_SPARK_LOG_LEVEL = "WARN"
DEFAULT_SPARK_MASTER_URL = "spark://spark-master:7077"
DEFAULT_SPARK_PACKAGES: Tuple[str, ...] = (
    "org.apache.spark:spark-hadoop-cloud_2.13:4.0.0",
    "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0",
    "org.mongodb.spark:mongo-spark-connector_2.13:10.5.0",
)
DEFAULT_MINIO_ENDPOINT = "http://minio.minio.svc.cluster.local:9000"
DEFAULT_MINIO_ACCESS_KEY = "minioadmin"
DEFAULT_MINIO_SECRET_KEY = "changeMe"
DEFAULT_DAGSTER_JOB_TTL_SECONDS = 0


@dataclass(frozen=True)
class MongoConfig:
    uri: str
    database: str
    collection: str


def mongo_config() -> MongoConfig:
    """Return the MongoDB connection settings."""
    return MongoConfig(
        uri=os.getenv(UPLOADS_MONGODB_URI_ENV, DEFAULT_MONGO_URI),
        database=os.getenv(UPLOADS_MONGODB_DATABASE_ENV, DEFAULT_MONGO_DATABASE),
        collection=os.getenv(UPLOADS_MONGODB_COLLECTION_ENV, DEFAULT_MONGO_COLLECTION),
    )


def _resolve_packages() -> Tuple[str, ...]:
    """Resolve Spark packages, allowing overrides via an environment variable."""
    override = os.getenv(SPARK_JARS_PACKAGES_ENV)
    if override:
        normalized = override.replace(",", " ").replace("\n", " ")
        packages = tuple(item for item in normalized.split() if item)
        if packages:
            return packages
    return DEFAULT_SPARK_PACKAGES


SPARK_PACKAGES: Tuple[str, ...] = _resolve_packages()


@dataclass(frozen=True)
class SparkConfig:
    master_url: str
    log_level: str


def spark_config() -> SparkConfig:
    """Return Spark-specific configuration."""
    return SparkConfig(
        master_url=os.getenv(SPARK_MASTER_URL_ENV, DEFAULT_SPARK_MASTER_URL),
        log_level=os.getenv(SPARK_LOG_LEVEL_ENV, DEFAULT_SPARK_LOG_LEVEL),
    )


@dataclass(frozen=True)
class MinioConfig:
    endpoint: str
    access_key: str
    secret_key: str

    @property
    def has_credentials(self) -> bool:
        return bool(self.access_key and self.secret_key)


def minio_config() -> MinioConfig:
    """Return the MinIO endpoint and credential configuration."""
    return MinioConfig(
        endpoint=os.getenv(MINIO_ENDPOINT_ENV, DEFAULT_MINIO_ENDPOINT),
        access_key=os.getenv(MINIO_ACCESS_KEY_ENV, DEFAULT_MINIO_ACCESS_KEY),
        secret_key=os.getenv(MINIO_SECRET_KEY_ENV, DEFAULT_MINIO_SECRET_KEY),
    )


def delta_output_path() -> str:
    """Return the Delta Lake output path."""
    return os.getenv(DELTA_LAKE_OUTPUT_PATH_ENV, DEFAULT_DELTA_OUTPUT_PATH)


def dagster_job_ttl_seconds() -> int:
    """Return the TTL (in seconds) after which Kubernetes cleans up run pods."""
    raw_value = os.getenv(DAGSTER_JOB_TTL_SECONDS_ENV)
    if raw_value is None:
        return DEFAULT_DAGSTER_JOB_TTL_SECONDS

    try:
        ttl = int(raw_value)
    except ValueError:
        return DEFAULT_DAGSTER_JOB_TTL_SECONDS

    return ttl if ttl >= 0 else DEFAULT_DAGSTER_JOB_TTL_SECONDS
