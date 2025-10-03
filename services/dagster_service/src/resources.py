"""Dagster resources used by the Mongo -> Delta job."""

from dagster import resource
from delta import configure_spark_with_delta_pip
from pymongo import MongoClient
from pymongo.collection import Collection
from pyspark.sql import SparkSession

from dagster_service.src import config


@resource
def mongo_collection_resource(_) -> Collection:  # type: ignore
    """Yield a MongoDB collection handle for the uploads dataset."""
    mongo_cfg = config.mongo_config()

    client = MongoClient(mongo_cfg.uri)  # type: ignore
    try:
        yield client[mongo_cfg.database][mongo_cfg.collection]  # type: ignore
    finally:
        client.close()


@resource
def spark_session_resource(_) -> SparkSession:  # type: ignore
    """Provide a Spark session configured for Delta Lake and optional MinIO access."""
    spark_cfg = config.spark_config()
    minio_cfg = config.minio_config()

    builder = (
        SparkSession.builder.appName("dagster-mongo-to-delta")
        .master(spark_cfg.master_url)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"
        )
    )

    if minio_cfg.endpoint:
        builder = (
            builder.config("spark.hadoop.fs.s3a.endpoint", minio_cfg.endpoint)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        )

    if minio_cfg.has_credentials:
        builder = (
            builder.config("spark.hadoop.fs.s3a.access.key", minio_cfg.access_key)
            .config("spark.hadoop.fs.s3a.secret.key", minio_cfg.secret_key)
            .config(
                "spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.SimpleAWscoredentialsProvider",
            )
        )

    spark = configure_spark_with_delta_pip(
        builder, extra_packages=list(config.SPARK_PACKAGES)
    ).getOrCreate()
    spark.sparkContext.setLogLevel(spark_cfg.log_level)
    try:
        yield spark  # type: ignore
    finally:
        spark.stop()


def resolve_output_path() -> str:
    """Return the configured Delta Lake output path."""
    return config.delta_output_path()
