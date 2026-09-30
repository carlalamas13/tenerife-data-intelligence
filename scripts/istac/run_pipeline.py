from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.ingestion.istac import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASET_ID,
    DEFAULT_FORMAT,
    get_latest_version,
    ingest_dataset,
)

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt" / "tenerife_dbt"


def run_command(
    command: list[str],
    description: str,
    cwd: Path,
) -> None:
    """Run a command and stop the pipeline if it fails."""
    LOGGER.info("%s", description)

    subprocess.run(
        command,
        cwd=cwd,
        check=True,
    )


def get_latest_loaded_version(
    dataset_id: str,
) -> str | None:
    """Return the latest dataset version loaded into RAW."""
    command = [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "tenerife",
        "-d",
        "tenerife",
        "-At",
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        (
            "SELECT source_version "
            "FROM raw.istac_ingestion_batch "
            f"WHERE dataset_code = '{dataset_id}' "
            "ORDER BY snapshot_date DESC, "
            "ingested_at DESC, "
            "ingestion_batch_id DESC "
            "LIMIT 1;"
        ),
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    version = result.stdout.strip()

    return version or None


def main() -> None:
    """Run the complete ISTAC ingestion pipeline."""

    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Run the complete ISTAC ingestion pipeline."
    )

    parser.add_argument(
        "--dataset-id",
        default=os.getenv(
            "ISTAC_DATASET_ID",
            DEFAULT_DATASET_ID,
        ),
        help="ISTAC dataset identifier.",
    )

    parser.add_argument(
        "--version",
        default=None,
        help=(
            "ISTAC dataset version. If omitted, the latest available "
            "version is detected automatically."
        ),
    )

    parser.add_argument(
        "--format",
        dest="fmt",
        default=os.getenv(
            "ISTAC_FORMAT",
            DEFAULT_FORMAT,
        ),
        help="Dataset format.",
    )

    parser.add_argument(
        "--raw-dir",
        default=os.getenv(
            "RAW_DIR",
            "data/raw",
        ),
        help="Raw data directory.",
    )

    args = parser.parse_args()

    base_url = os.getenv(
        "ISTAC_BASE_URL",
        DEFAULT_BASE_URL,
    )

    explicit_version = args.version is not None

    if explicit_version:
        version = args.version
        LOGGER.info(
            "Using explicitly requested ISTAC version: %s",
            version,
        )
    else:
        version = get_latest_version(
            dataset_id=args.dataset_id,
            base_url=base_url,
        )

        latest_loaded_version = get_latest_loaded_version(
            dataset_id=args.dataset_id,
        )

        LOGGER.info(
            "Latest loaded ISTAC version: %s",
            latest_loaded_version or "none",
        )

        if latest_loaded_version == version:
            LOGGER.info(
                "No new ISTAC version available. "
                "Latest version %s is already loaded.",
                version,
            )
            return

        LOGGER.info(
            "New ISTAC version detected: %s",
            version,
        )

    LOGGER.info(
        "Using ISTAC dataset %s version %s.",
        args.dataset_id,
        version,
    )

    # Step 1: download the dataset and generate its manifest.
    LOGGER.info(
        "Step 1/4: downloading ISTAC dataset."
    )

    dataset_path, manifest_path = ingest_dataset(
        dataset_id=args.dataset_id,
        version=version,
        fmt=args.fmt,
        raw_dir=args.raw_dir,
        base_url=base_url,
    )

    LOGGER.info(
        "Dataset path: %s",
        dataset_path,
    )
    LOGGER.info(
        "Manifest path: %s",
        manifest_path,
    )

    # Step 2: run the quality gate against the exact snapshot.
    run_command(
        [
            sys.executable,
            "-m",
            "scripts.istac.validate_dataset",
            "--dataset",
            str(dataset_path),
        ],
        "Step 2/4: running ISTAC quality gate.",
        PROJECT_ROOT,
    )

    # Step 3: load the validated snapshot into RAW.
    run_command(
        [
            sys.executable,
            "scripts/istac/load_raw.py",
            "--manifest",
            str(manifest_path),
        ],
        "Step 3/4: loading validated snapshot into RAW.",
        PROJECT_ROOT,
    )

    # Step 4: rebuild all dbt models and tests.
    run_command(
        [
            "dbt",
            "build",
        ],
        "Step 4/4: running dbt build.",
        DBT_PROJECT_DIR,
    )

    LOGGER.info(
        "ISTAC pipeline completed successfully."
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    main()