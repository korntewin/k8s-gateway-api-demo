"""Convenience entrypoint to trigger the Dagster job on demand."""

from dagster_service.src.jobs import mongo_to_delta_job


def run_once() -> None:
    """Execute the mongo_to_delta job once using in-process resources."""
    mongo_to_delta_job.execute_in_process()


if __name__ == "__main__":  # pragma: no cover
    run_once()
